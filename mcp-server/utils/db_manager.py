"""
Thread-safe JSON database manager with file locking.
Acts as a lightweight persistence layer for healing records.
"""
import json
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import portalocker

from utils.logger import get_logger
from config.settings import settings

logger = get_logger("db_manager", settings.log_file, settings.log_level)

# ── File paths ────────────────────────────────────────────────────────────────
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
    Persist a healing decision record to healed_locators.json.
    Returns the generated healing_id.
    """
    healing_id = record.get("healing_id") or str(uuid.uuid4())
    record["healing_id"] = healing_id
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    records = _read_json(HEALED_LOCATORS_FILE)
    records.append(record)
    _write_json(HEALED_LOCATORS_FILE, records)

    logger.debug(f"Saved healing record [{healing_id}]")
    return healing_id


def save_failure_log(log_entry: Dict[str, Any]) -> None:
    """Append a failure log entry to failure_logs.json."""
    log_entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    logs = _read_json(FAILURE_LOGS_FILE)
    logs.append(log_entry)
    _write_json(FAILURE_LOGS_FILE, logs)


def save_confidence_score(score_entry: Dict[str, Any]) -> None:
    """Append a confidence score entry to confidence_scores.json."""
    score_entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    scores = _read_json(CONFIDENCE_SCORES_FILE)
    scores.append(score_entry)
    _write_json(CONFIDENCE_SCORES_FILE, scores)


def get_all_healing_records() -> List[Dict]:
    """Return all healing records sorted newest-first."""
    records = _read_json(HEALED_LOCATORS_FILE)
    return sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)


def get_all_failure_logs() -> List[Dict]:
    return _read_json(FAILURE_LOGS_FILE)


def get_all_confidence_scores() -> List[Dict]:
    return _read_json(CONFIDENCE_SCORES_FILE)


def get_healing_record_by_id(healing_id: str) -> Optional[Dict]:
    """Fetch a single healing record by its ID."""
    records = _read_json(HEALED_LOCATORS_FILE)
    for r in records:
        if r.get("healing_id") == healing_id:
            return r
    return None


def get_confidence_report_data() -> Dict[str, Any]:
    """Aggregate statistics for the confidence report endpoint."""
    records = _read_json(HEALED_LOCATORS_FILE)
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
