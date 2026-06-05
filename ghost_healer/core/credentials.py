"""
Credential store — install-only SDK access + optional user override.

Built-in public key is bundled with the SDK; no manual login required for hosted Brain.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_BRAIN_URL = "https://ghost-healer-brain.onrender.com"
BUILTIN_API_KEY = "gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9"


def ghost_dir() -> Path:
    return Path.home() / ".ghost"


def credentials_path() -> Path:
    return ghost_dir() / "credentials.json"


def load_global_credentials() -> Optional[Dict[str, Any]]:
    path = credentials_path()
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_global_credentials(
    api_key: str,
    brain_url: str = DEFAULT_BRAIN_URL,
    tenant_id: str = "default",
    project_id: str = "default",
    source: str = "user",
) -> Dict[str, Any]:
    ghost_dir().mkdir(parents=True, exist_ok=True)
    payload = {
        "api_key": api_key,
        "brain_url": brain_url,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "source": source,
    }
    path = credentials_path()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return payload


def ensure_builtin_credentials() -> Dict[str, Any]:
    existing = load_global_credentials()
    if existing:
        return existing
    return save_global_credentials(
        api_key=BUILTIN_API_KEY,
        brain_url=DEFAULT_BRAIN_URL,
        tenant_id="sdk",
        project_id="default",
        source="builtin",
    )


def apply_global_credentials() -> None:
    """Apply saved or built-in SDK credentials (does not override existing env)."""
    creds = load_global_credentials()
    if creds:
        if creds.get("api_key") and not os.environ.get("GHOST_API_KEY"):
            os.environ["GHOST_API_KEY"] = str(creds["api_key"])
        if creds.get("brain_url") and not os.environ.get("GHOST_BRAIN_URL"):
            os.environ["GHOST_BRAIN_URL"] = str(creds["brain_url"])
        if creds.get("tenant_id") and not os.environ.get("GHOST_TENANT_ID"):
            os.environ["GHOST_TENANT_ID"] = str(creds["tenant_id"])
        if creds.get("project_id") and not os.environ.get("GHOST_PROJECT_ID"):
            os.environ["GHOST_PROJECT_ID"] = str(creds["project_id"])

    if not os.environ.get("GHOST_API_KEY"):
        os.environ["GHOST_API_KEY"] = BUILTIN_API_KEY
    if not os.environ.get("GHOST_BRAIN_URL"):
        os.environ["GHOST_BRAIN_URL"] = DEFAULT_BRAIN_URL
