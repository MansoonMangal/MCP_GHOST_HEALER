"""
Auto-activation for non-pytest Python runners (e.g. `python test_demo.py`).

Set GHOST_AUTO_ACTIVATE=1 or install ghost-healer — module is imported on package load
when env is set.
"""
import os
import logging

logger = logging.getLogger("GhostAutoload")

if os.environ.get("GHOST_AUTO_ACTIVATE", "1") == "1":
    try:
        import ghost_healer.adapters.playwright  # noqa: F401 — registers hooks if playwright present
        logger.debug("[GHOST] autoload: playwright hooks registered")
    except Exception:
        pass
