"""
👻 Ghost Healer: Enterprise AI Self-Healing Framework
"""

__version__ = "1.0.0"

from ghost_healer.core.engine import GhostEngine
from ghost_healer.adapters.playwright import protect_page

__all__ = ["GhostEngine", "protect_page"]
