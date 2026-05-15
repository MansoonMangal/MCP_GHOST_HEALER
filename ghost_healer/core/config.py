"""
Ghost Healer — Centralized Configuration (Phase 9)

Reads ghost.yaml from the project root.
All settings have safe defaults so the framework works out of the box.
"""
import os
import yaml
import logging
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger("GhostConfig")


class MCPServerConfig(BaseModel):
    url: str = "http://localhost:8000"
    timeout: int = 30
    confidence_threshold: float = 0.5    # Minimum score (0–1) to trust a heal


class HealingConfig(BaseModel):
    mode: str = "runtime"                # runtime | suggestion | strict
    auto_patch: bool = True              # Rewrite source files after healing
    cache_enabled: bool = True           # Use SQLite cache (.ghost_cache.db)
    max_retries: int = 3                 # Retries on Brain connectivity failures
    retry_wait_seconds: int = 5          # Base wait between retries (exponential)
    framework: str = "playwright-python" # Framework label for reporting


class ReportingConfig(BaseModel):
    output_dir: str = "reports/ghost"   # Directory for JSON reports
    format: str = "json"
    save_traces: bool = True            # Include Brain execution trace in reports
    min_confidence_to_log: float = 0.0  # Only log events above this confidence


class GhostConfig(BaseModel):
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    healing: HealingConfig = Field(default_factory=HealingConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)


def load_config(config_path: Optional[str] = None) -> GhostConfig:
    """
    Load ghost.yaml from:
    1. Explicit path (if provided)
    2. GHOST_CONFIG env var
    3. ./ghost.yaml in current working directory
    4. Safe defaults if no file found
    """
    path = (
        config_path
        or os.environ.get("GHOST_CONFIG")
        or "ghost.yaml"
    )

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            config = GhostConfig(**data)
            logger.debug(f"[Config] Loaded from {path}")
            return config
        except Exception as e:
            logger.warning(f"[Config] Failed to parse {path}: {e}. Using defaults.")

    logger.debug("[Config] ghost.yaml not found — using defaults.")
    return GhostConfig()


# Global config instance — loaded once at import time
settings = load_config()
