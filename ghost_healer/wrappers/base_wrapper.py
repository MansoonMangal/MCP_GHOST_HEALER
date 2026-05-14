import logging
import time
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from playwright.sync_api import Page, Locator
from ghost_framework.wrappers.safe_locator import SafeLocator
from ghost_framework.wrappers.models import HealResult
from ghost_framework.utils.element_cache import element_memory
from ghost_framework.utils.source_healer import SourceHealer
from ghost_framework.config.framework_config import config

logger = logging.getLogger("BaseWrapper")

def execute_safe_action(
    page: Page,
    selector: str,
    action_name: str,
    action_fn: Callable[[Locator], Any],
    hints: Optional[Dict[str, Any]] = None,
) -> Optional[HealResult]:
    """
    The advanced orchestrator for all safe actions.
    Handles logging, healing, and visual feedback.
    """
    # ── Step 1: Check Memory for hints ──────────────────────────────
    if not hints:
        hints = element_memory.get_memory(selector) or {}
    else:
        # Merge provided hints with memory
        memory = element_memory.get_memory(selector) or {}
        hints = {**memory, **hints}

    logger.info(f"[{action_name}] Attempting: '{selector}'")
    
    safe = SafeLocator(page)
    locator, heal_result = safe.locate(selector, action=action_name, hints=hints)

    # ── Step 2: Auto-Correction (Rewrite the script!) ──────────
    if heal_result:
        SourceHealer.apply_fix(
            old_selector=selector,
            new_selector=heal_result.healed_locator
        )

        # PREMIUM FEATURE: Visual Highlighting of healed element
        if config.enable_visual_highlight:
            try:
                logger.info(f" [HEALED] '{selector}' -> {heal_result.healed_locator} (Score: {heal_result.confidence_score:.1f})")
                _highlight_element(page, heal_result.healed_locator)
            except Exception:
                pass
    else:
        # ── Step 3: Learning Phase (If it worked directly, learn it!) ──
        if config.enable_smart_memory:
            try:
                _learn_from_element(page, selector, locator)
            except Exception:
                pass

    # Execute the actual action
    action_fn(locator)
    return heal_result

def safe_perform(
    page: Page,
    selector: str,
    method: str,
    hints: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Optional[HealResult]:
    """Universal Wrapper for any Playwright action."""
    def action(loc: Locator):
        func = getattr(loc, method)
        return func(**kwargs)

    return execute_safe_action(page, selector, method, action, hints)

def _learn_from_element(page: Page, selector: str, locator: Locator):
    try:
        # Use absolute path relative to the framework root
        framework_root = Path(__file__).resolve().parent.parent
        agent_path = framework_root / "assets" / "heal_qa_agent.js"
        with open(agent_path, "r") as f:
            agent_js = f.read()
        page.evaluate(agent_js)
        dna = page.evaluate(f"HealQA.getElementDNA('{selector}')")
        if dna:
            element_memory.learn(selector, dna)
    except Exception: pass

def _highlight_element(page: Page, selector: str):
    try:
        framework_root = Path(__file__).resolve().parent.parent
        agent_path = framework_root / "assets" / "heal_qa_agent.js"
        with open(agent_path, "r") as f:
            agent_js = f.read()
        page.evaluate(agent_js)
        page.evaluate(f"HealQA.highlight('{selector}')")
    except Exception: pass
