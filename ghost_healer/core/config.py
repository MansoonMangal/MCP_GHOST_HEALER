"""
Ghost Healer — Centralized Configuration (Phase 9)

Reads ghost.yaml from the project root (walks parent directories from cwd).
All settings have safe defaults so the framework works out of the box.
"""
import os
import yaml
import logging
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Tuple

logger = logging.getLogger("GhostConfig")

_MAX_CONFIG_WALK = 20


class MCPServerConfig(BaseModel):
    url: str = "https://ghost-healer-brain.onrender.com"
    timeout: int = 30
    confidence_threshold: float = 0.5    # Minimum score (0–1) to trust a heal
    protocol: str = "mcp-first"          # mcp-first | mcp | rest
    api_key: str = ""                    # GHOST_API_KEY override via env
    tenant_id: str = "default"
    project_id: str = "default"

    @field_validator("confidence_threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        return v


class HealingConfig(BaseModel):
    mode: str = "runtime"                # runtime | suggestion | strict | approval
    auto_patch: bool = True              # Rewrite source files after healing
    cache_enabled: bool = True           # Use SQLite cache (.ghost_cache.db)
    max_retries: int = 3                 # Retries on Brain connectivity failures
    retry_wait_seconds: int = 5          # Base wait between retries (exponential)
    framework: str = "playwright-python" # Framework label for reporting
    selenium_fixture_names: List[str] = Field(
        default_factory=lambda: ["driver", "browser", "webdriver", "selenium_driver"]
    )
    selenium_fixture_name: str = "driver"  # legacy single name


class ReportingConfig(BaseModel):
    output_dir: str = "reports/ghost"   # Directory for JSON reports
    format: str = "json"
    save_traces: bool = True            # Include Brain execution trace in reports
    min_confidence_to_log: float = 0.0  # Only log events above this confidence


class GhostConfig(BaseModel):
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    healing: HealingConfig = Field(default_factory=HealingConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    config_dir: str = ""  # Directory where ghost.yaml was found (or project root)


def _walk_parents(start: Path) -> List[Path]:
    dirs: List[Path] = []
    current = start.resolve()
    for _ in range(_MAX_CONFIG_WALK):
        dirs.append(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return dirs


def find_ghost_yaml(start_dir: Optional[str] = None) -> Optional[str]:
    """Walk up from start_dir (or cwd) to find ghost.yaml (mirrors TS SDK)."""
    for directory in _walk_parents(Path(start_dir or os.getcwd())):
        candidate = directory / "ghost.yaml"
        if candidate.is_file():
            return str(candidate)
    return None


def find_project_root(start_dir: Optional[str] = None) -> str:
    """Walk up to ghost.yaml or .git; otherwise use cwd."""
    for directory in _walk_parents(Path(start_dir or os.getcwd())):
        if (directory / "ghost.yaml").is_file() or (directory / ".git").exists():
            return str(directory)
    return os.getcwd()


def resolve_config_path(config_path: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Return (yaml_path or None, config_dir).
    Priority: explicit path > GHOST_CONFIG > walk-up ghost.yaml > project root.
    """
    explicit = config_path or os.environ.get("GHOST_CONFIG")
    if explicit:
        resolved = Path(explicit).resolve()
        if resolved.is_file():
            return str(resolved), str(resolved.parent)
        if resolved.is_dir() and (resolved / "ghost.yaml").is_file():
            yaml_path = resolved / "ghost.yaml"
            return str(yaml_path), str(resolved)
        logger.warning(f"[Config] Path not found: {explicit}")

    found = find_ghost_yaml()
    if found:
        return found, str(Path(found).parent)

    root = find_project_root()
    return None, root


def _load_dotenv(start_dir: Optional[str] = None) -> None:
    """Load credentials + .env from project root."""
    from ghost_healer.core.credentials import apply_global_credentials

    apply_global_credentials()

    root = Path(find_project_root(start_dir))
    env_name = os.environ.get("ENV_FILE", ".env")
    for name in (env_name, ".env"):
        env_path = root / name
        if not env_path.is_file():
            continue
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and not os.environ.get(key):
                    os.environ[key] = value
        except OSError:
            pass
        break


def load_config(config_path: Optional[str] = None) -> GhostConfig:
    """
    Load ghost.yaml from:
    1. Explicit path (if provided)
    2. GHOST_CONFIG env var
    3. ghost.yaml found by walking up from cwd (up to 20 levels)
    4. Safe defaults if no file found (config_dir = project root or cwd)
    """
    _load_dotenv()
    yaml_path, config_dir = resolve_config_path(config_path)

    env_api_key = os.environ.get("GHOST_API_KEY", "")
    env_brain_url = os.environ.get("GHOST_BRAIN_URL") or os.environ.get("MCP_SERVER_URL")

    if yaml_path and os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            config = GhostConfig(**data)
            config.config_dir = config_dir
            if env_brain_url:
                config.mcp_server.url = env_brain_url
            if env_api_key:
                config.mcp_server.api_key = env_api_key
            logger.debug(f"[Config] Loaded from {yaml_path} (config_dir={config_dir})")
            return config
        except Exception as e:
            logger.warning(f"[Config] Failed to parse {yaml_path}: {e}. Using defaults.")

    logger.debug(f"[Config] ghost.yaml not found — using defaults (config_dir={config_dir}).")
    config = GhostConfig()
    config.config_dir = config_dir
    if env_brain_url:
        config.mcp_server.url = env_brain_url
    if env_api_key:
        config.mcp_server.api_key = env_api_key
    return config


# Global config instance — loaded once at import time
settings = load_config()
