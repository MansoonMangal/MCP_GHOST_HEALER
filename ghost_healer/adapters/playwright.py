"""
Ghost Healer — Playwright Adapter (Full Coverage)

Patches ALL major Playwright Page actions with AI self-healing.
The user calls standard Playwright — Ghost intercepts silently.
"""
import types
import time
import logging
from playwright.sync_api import Page
from ghost_healer.core.engine import ghost_engine
from ghost_healer.utils.reporter import reporter

logger = logging.getLogger("GhostPlaywright")


# ── Internal helper ───────────────────────────────────────────────────────────

def _heal_and_retry(page: Page, selector: str, action: str, original_fn, *args, **kwargs):
    """
    Core heal-and-retry pattern shared across all patched methods.
    1. Try original call (2s timeout to fail fast)
    2. On failure, request healed locator from AI Brain
    3. If healed, log it, retry with new selector
    4. If not healed, re-raise original error
    """
    try:
        return original_fn(selector, *args, **kwargs)
    except Exception as original_error:
        start = time.time()
        logger.warning(f"[GHOST] {action} failed for '{selector}'. Requesting AI heal...")
        healed = ghost_engine.get_healed_locator(selector, action, page.content())
        duration = (time.time() - start) * 1000

        if healed:
            logger.info(f"[GHOST] Healed '{selector}' → '{healed}' (action={action})")
            reporter.log_healing(selector, healed, 0.0, duration)
            return original_fn(healed, *args, **kwargs)

        logger.error(f"[GHOST] Could not heal '{selector}'. Raising original error.")
        raise original_error


# ── Patch factory ─────────────────────────────────────────────────────────────

def _make_selector_patch(page: Page, method_name: str, action: str):
    """
    Generic factory that creates a self-healing wrapper for any
    Playwright Page method that takes a selector as its first argument.
    """
    original_fn = getattr(page, method_name)

    def patched(self, selector, *args, **kwargs):
        # Inject a short timeout on the first attempt to fail fast
        if "timeout" not in kwargs:
            kwargs["timeout"] = 2000
        return _heal_and_retry(page, selector, action, original_fn, *args, **kwargs)

    return types.MethodType(patched, page)


# ── Main entry point ──────────────────────────────────────────────────────────

def protect_page(page: Page) -> Page:
    """
    👻 Patches a Playwright Page instance with AI Self-Healing.

    Supported actions (all invisible to the test author):
      click, fill, hover, check, uncheck, dblclick,
      press, select_option, wait_for_selector

    Usage in conftest.py:
        from ghost_healer import protect_page

        @pytest.fixture(autouse=True)
        def ghost_mode(page):
            protect_page(page)
            yield
    """
    actions_to_patch = {
        "click":             "click",
        "fill":              "fill",
        "hover":             "hover",
        "check":             "check",
        "uncheck":           "uncheck",
        "dblclick":          "click",
        "press":             "press",
        "select_option":     "select",
        "wait_for_selector": "wait",
    }

    for method_name, action_type in actions_to_patch.items():
        if hasattr(page, method_name):
            setattr(page, method_name, _make_selector_patch(page, method_name, action_type))
            logger.debug(f"[GHOST] Patched page.{method_name}()")

    logger.info("[GHOST] Page protection active. AI healing enabled for all actions.")
    return page
