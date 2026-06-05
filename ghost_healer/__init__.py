"""
👻 Ghost Healer v1.1.0 — Universal AI Self-Healing Framework

Public API:
  protect_page(page)    → Playwright self-healing (Python)
  protect_driver(driver) → Selenium self-healing (Python)
  GhostEngine           → Core AI healing orchestrator
"""
__version__ = "1.2.3"

try:
    from ghost_healer.core.credentials import ensure_builtin_credentials

    ensure_builtin_credentials()
except Exception:
    pass

try:
    import ghost_healer.autoload  # noqa: F401
except Exception:
    pass

from ghost_healer.core.engine import GhostEngine
from ghost_healer.adapters.playwright import protect_page
from ghost_healer.adapters.selenium import protect_driver

__all__ = [
    "GhostEngine",
    "protect_page",
    "protect_driver",
]
