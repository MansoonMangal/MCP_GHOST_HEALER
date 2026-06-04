import sqlite3
import os
import logging
from typing import Optional

from ghost_healer.core.config import settings

logger = logging.getLogger("GhostCache")


def _default_cache_path() -> str:
    base = settings.config_dir or os.getcwd()
    return os.path.join(base, ".ghost_cache.db")


class HealingCache:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _default_cache_path()
        self._init_db()

    def _init_db(self):
        if not settings.healing.cache_enabled:
            return
        parent = os.path.dirname(self.db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locator_cache (
                    original_selector TEXT PRIMARY KEY,
                    healed_selector TEXT NOT NULL,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get(self, selector: str) -> Optional[str]:
        if not settings.healing.cache_enabled:
            return None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT healed_selector FROM locator_cache WHERE original_selector = ?",
                    (selector,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def get_with_confidence(self, selector: str) -> tuple[Optional[str], float]:
        if not settings.healing.cache_enabled:
            return (None, 0.0)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT healed_selector, confidence FROM locator_cache WHERE original_selector = ?",
                    (selector,)
                )
                row = cursor.fetchone()
                return (row[0], row[1] if row[1] is not None else 0.0) if row else (None, 0.0)
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return (None, 0.0)

    def set(self, original: str, healed: str, confidence: float):
        if not settings.healing.cache_enabled:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO locator_cache (original_selector, healed_selector, confidence) VALUES (?, ?, ?)",
                    (original, healed, confidence)
                )
        except Exception as e:
            logger.error(f"Cache write error: {e}")


# Global cache instance — anchored to settings.config_dir
cache = HealingCache()
