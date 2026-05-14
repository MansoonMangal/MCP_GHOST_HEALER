import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger("GhostCache")

class HealingCache:
    def __init__(self, db_path: str = ".ghost_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
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

    def set(self, original: str, healed: str, confidence: float):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO locator_cache (original_selector, healed_selector, confidence) VALUES (?, ?, ?)",
                    (original, healed, confidence)
                )
        except Exception as e:
            logger.error(f"Cache write error: {e}")

# Global cache instance
cache = HealingCache()
