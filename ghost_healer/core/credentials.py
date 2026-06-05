"""
Enterprise credential store — ~/.ghost/credentials.json

One-time login; all projects on the machine inherit the API key.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_BRAIN_URL = "https://ghost-healer-brain.onrender.com"


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
) -> Dict[str, Any]:
    ghost_dir().mkdir(parents=True, exist_ok=True)
    payload = {
        "api_key": api_key,
        "brain_url": brain_url,
        "tenant_id": tenant_id,
        "project_id": project_id,
    }
    path = credentials_path()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return payload


def apply_global_credentials() -> None:
    """Apply ~/.ghost/credentials.json to os.environ (does not override existing)."""
    creds = load_global_credentials()
    if not creds:
        return
    if creds.get("api_key") and not os.environ.get("GHOST_API_KEY"):
        os.environ["GHOST_API_KEY"] = str(creds["api_key"])
    if creds.get("brain_url") and not os.environ.get("GHOST_BRAIN_URL"):
        os.environ["GHOST_BRAIN_URL"] = str(creds["brain_url"])
    if creds.get("tenant_id") and not os.environ.get("GHOST_TENANT_ID"):
        os.environ["GHOST_TENANT_ID"] = str(creds["tenant_id"])
    if creds.get("project_id") and not os.environ.get("GHOST_PROJECT_ID"):
        os.environ["GHOST_PROJECT_ID"] = str(creds["project_id"])
