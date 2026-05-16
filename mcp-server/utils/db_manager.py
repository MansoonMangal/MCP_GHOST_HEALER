"""
Thread-safe database manager — Hybrid Storage Layer.

Production (Render): Uses MongoDB when MONGO_URI env var is set.
Local Development:   Falls back to thread-safe JSON files with file locking.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import portalocker

from utils.logger import get_logger
from config.settings import settings

logger = get_logger("db_manager", settings.log_file, settings.log_level)

# ── Detect storage backend ────────────────────────────────────────────────────
_USE_MONGO = bool(settings.mongo_uri)
_mongo_db = None

if _USE_MONGO:
    try:
        from pymongo import MongoClient
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        _mongo_db = _client.get_database("ghost_healer")
        logger.info("✅ MongoDB connected — using persistent storage (production mode)")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB connection failed, falling back to JSON files: {e}")
        _USE_MONGO = False
else:
    logger.info("📁 MONGO_URI not set — using local JSON file storage (dev mode)")

# ── JSON File paths (dev fallback) ────────────────────────────────────────────
DB_PATH = Path(settings.db_path)
HEALED_LOCATORS_FILE = DB_PATH / "healed_locators.json"
FAILURE_LOGS_FILE = DB_PATH / "failure_logs.json"
CONFIDENCE_SCORES_FILE = DB_PATH / "confidence_scores.json"


def _ensure_db_files() -> None:
    """Initialize empty JSON arrays if database files don't exist."""
    DB_PATH.mkdir(parents=True, exist_ok=True)
    for filepath in [HEALED_LOCATORS_FILE, FAILURE_LOGS_FILE, CONFIDENCE_SCORES_FILE]:
        if not filepath.exists():
            filepath.write_text("[]", encoding="utf-8")


def _read_json(filepath: Path) -> List[Dict]:
    """Read JSON file with shared lock (allows concurrent reads)."""
    _ensure_db_files()
    with open(filepath, "r", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LOCK_SH)
        try:
            content = f.read()
            return json.loads(content) if content.strip() else []
        finally:
            portalocker.unlock(f)


def _write_json(filepath: Path, data: List[Dict]) -> None:
    """Write JSON file with exclusive lock (prevents concurrent writes)."""
    with open(filepath, "w", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
        finally:
            portalocker.unlock(f)


# ── Public API ────────────────────────────────────────────────────────────────

def save_healing_record(record: Dict[str, Any]) -> str:
    """
    Persist a healing decision record.
    Returns the generated healing_id.
    """
    healing_id = record.get("healing_id") or str(uuid.uuid4())
    record["healing_id"] = healing_id
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    if _USE_MONGO:
        _mongo_db["healed_locators"].insert_one({**record, "_id": healing_id})
    else:
        records = _read_json(HEALED_LOCATORS_FILE)
        records.append(record)
        _write_json(HEALED_LOCATORS_FILE, records)

    logger.debug(f"Saved healing record [{healing_id}]")
    return healing_id


def save_failure_log(log_entry: Dict[str, Any]) -> None:
    """Append a failure log entry."""
    log_entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    if _USE_MONGO:
        _mongo_db["failure_logs"].insert_one(log_entry)
    else:
        logs = _read_json(FAILURE_LOGS_FILE)
        logs.append(log_entry)
        _write_json(FAILURE_LOGS_FILE, logs)


def save_confidence_score(score_entry: Dict[str, Any]) -> None:
    """Append a confidence score entry."""
    score_entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    if _USE_MONGO:
        _mongo_db["confidence_scores"].insert_one(score_entry)
    else:
        scores = _read_json(CONFIDENCE_SCORES_FILE)
        scores.append(score_entry)
        _write_json(CONFIDENCE_SCORES_FILE, scores)


def get_all_healing_records() -> List[Dict]:
    """Return all healing records sorted newest-first."""
    if _USE_MONGO:
        docs = list(_mongo_db["healed_locators"].find({}, {"_id": 0}).sort("timestamp", -1))
        return docs
    records = _read_json(HEALED_LOCATORS_FILE)
    return sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)


def get_healing_record_by_id(healing_id: str) -> Optional[Dict]:
    """Fetch a single healing record by its ID."""
    if _USE_MONGO:
        doc = _mongo_db["healed_locators"].find_one({"healing_id": healing_id}, {"_id": 0})
        return doc
    records = _read_json(HEALED_LOCATORS_FILE)
    for r in records:
        if r.get("healing_id") == healing_id:
            return r
    return None


def get_confidence_report_data() -> Dict[str, Any]:
    """Aggregate statistics for the confidence report endpoint."""
    records = get_all_healing_records()

    if not records:
        return {
            "total_healed": 0, "auto_heal_count": 0, "manual_review_count": 0,
            "fail_count": 0, "avg_confidence_score": 0.0,
            "high_confidence_count": 0, "medium_confidence_count": 0, "low_confidence_count": 0,
            "success_rate_percent": 0.0, "score_distribution": [], "most_unstable_locators": []
        }

    auto_heal = sum(1 for r in records if r.get("decision") == "AUTO_HEAL")
    manual = sum(1 for r in records if r.get("decision") == "MANUAL_REVIEW")
    fail = sum(1 for r in records if r.get("decision") == "FAIL")

    scores = [r.get("confidence_score", 0) for r in records]
    avg_score = sum(scores) / len(scores) if scores else 0

    high = sum(1 for r in records if r.get("confidence_level") == "HIGH")
    medium = sum(1 for r in records if r.get("confidence_level") == "MEDIUM")
    low = sum(1 for r in records if r.get("confidence_level") == "LOW")

    success_rate = (auto_heal / len(records) * 100) if records else 0

    # Score distribution: bucket into 10-point ranges
    buckets: Dict[str, int] = {}
    for score in scores:
        bucket = f"{int(score // 10) * 10}-{int(score // 10) * 10 + 9}"
        buckets[bucket] = buckets.get(bucket, 0) + 1
    score_dist = [{"range": k, "count": v} for k, v in sorted(buckets.items())]

    # Most unstable locators: top 10 by frequency of failure
    locator_counts: Dict[str, int] = {}
    for r in records:
        loc = r.get("original_locator", "unknown")
        locator_counts[loc] = locator_counts.get(loc, 0) + 1
    unstable = sorted(
        [{"locator": k, "failure_count": v} for k, v in locator_counts.items()],
        key=lambda x: x["failure_count"], reverse=True
    )[:10]

    return {
        "total_healed": len(records),
        "auto_heal_count": auto_heal,
        "manual_review_count": manual,
        "fail_count": fail,
        "avg_confidence_score": round(avg_score, 2),
        "high_confidence_count": high,
        "medium_confidence_count": medium,
        "low_confidence_count": low,
        "success_rate_percent": round(success_rate, 2),
        "score_distribution": score_dist,
        "most_unstable_locators": unstable
    }
