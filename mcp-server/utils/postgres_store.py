"""
PostgreSQL storage for Render-managed Postgres (DATABASE_URL / postgresql://).
Records stored as JSONB documents, mirroring MongoDB collections.
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("postgres_store")

_conn = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS healed_locators (
    healing_id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS failure_logs (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS confidence_scores (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS heal_feedback (
    feedback_id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pending_fixes (
    pending_id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_healed_locators_ts ON healed_locators ((data->>'timestamp'));
CREATE INDEX IF NOT EXISTS idx_pending_fixes_status ON pending_fixes ((data->>'status'));
"""


def connect(uri: str) -> bool:
    """Connect and ensure schema. Returns True on success."""
    global _conn
    try:
        import psycopg2

        _conn = psycopg2.connect(uri)
        _conn.autocommit = True
        with _conn.cursor() as cur:
            for statement in _SCHEMA_SQL.split(";"):
                stmt = statement.strip()
                if stmt:
                    cur.execute(stmt)
        logger.info("PostgreSQL connected — using persistent storage (Render Postgres)")
        return True
    except Exception as exc:
        logger.warning(f"PostgreSQL connection failed: {exc}")
        _conn = None
        return False


def is_connected() -> bool:
    return _conn is not None


def _json(record: Dict[str, Any]) -> str:
    return json.dumps(record, default=str)


def save_healing_record(record: Dict[str, Any]) -> str:
    healing_id = record["healing_id"]
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO healed_locators (healing_id, data)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (healing_id) DO UPDATE SET data = EXCLUDED.data
            """,
            (healing_id, _json(record)),
        )
    return healing_id


def save_failure_log(log_entry: Dict[str, Any]) -> None:
    with _conn.cursor() as cur:
        cur.execute(
            "INSERT INTO failure_logs (data) VALUES (%s::jsonb)",
            (_json(log_entry),),
        )


def save_confidence_score(score_entry: Dict[str, Any]) -> None:
    with _conn.cursor() as cur:
        cur.execute(
            "INSERT INTO confidence_scores (data) VALUES (%s::jsonb)",
            (_json(score_entry),),
        )


def get_all_healing_records() -> List[Dict]:
    with _conn.cursor() as cur:
        cur.execute(
            """
            SELECT data FROM healed_locators
            ORDER BY (data->>'timestamp') DESC NULLS LAST
            """
        )
        rows = cur.fetchall()
    return [row[0] for row in rows]


def get_healing_record_by_id(healing_id: str) -> Optional[Dict]:
    with _conn.cursor() as cur:
        cur.execute(
            "SELECT data FROM healed_locators WHERE healing_id = %s",
            (healing_id,),
        )
        row = cur.fetchone()
    return row[0] if row else None


def save_heal_feedback(entry: Dict[str, Any]) -> None:
    feedback_id = entry["feedback_id"]
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO heal_feedback (feedback_id, data)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (feedback_id) DO UPDATE SET data = EXCLUDED.data
            """,
            (feedback_id, _json(entry)),
        )


def get_feedback_rows(
    tenant_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[Dict]:
    query = "SELECT data FROM heal_feedback WHERE 1=1"
    params: List[Any] = []
    if tenant_id:
        query += " AND data->>'tenant_id' = %s"
        params.append(tenant_id)
    if project_id:
        query += " AND data->>'project_id' = %s"
        params.append(project_id)
    with _conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    return [row[0] for row in rows]


def save_pending_fix(entry: Dict[str, Any]) -> None:
    pending_id = entry["pending_id"]
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO pending_fixes (pending_id, data)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (pending_id) DO UPDATE SET data = EXCLUDED.data
            """,
            (pending_id, _json(entry)),
        )


def list_pending_fixes(
    tenant_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: str = "pending_review",
    limit: int = 100,
) -> List[Dict]:
    query = "SELECT data FROM pending_fixes WHERE 1=1"
    params: List[Any] = []
    if status:
        query += " AND data->>'status' = %s"
        params.append(status)
    if tenant_id:
        query += " AND data->>'tenant_id' = %s"
        params.append(tenant_id)
    if project_id:
        query += " AND data->>'project_id' = %s"
        params.append(project_id)
    query += " ORDER BY (data->>'timestamp') DESC NULLS LAST LIMIT %s"
    params.append(limit)
    with _conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    return [row[0] for row in rows]


def update_pending_fix_status(pending_id: str, status: str) -> bool:
    updated_at = datetime.now(timezone.utc).isoformat()
    with _conn.cursor() as cur:
        cur.execute(
            """
            UPDATE pending_fixes
            SET data = data || %s::jsonb
            WHERE pending_id = %s
            """,
            (_json({"status": status, "updated_at": updated_at}), pending_id),
        )
        return cur.rowcount > 0
