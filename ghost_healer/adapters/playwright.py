"""
Ghost Healer — Playwright Adapter (Full Coverage)

Patches Playwright Page AND Locator actions with AI self-healing.
"""
import types
import time
import logging
from playwright.sync_api import Page, Locator
from ghost_healer.core.engine import ghost_engine
from ghost_healer.utils.reporter import reporter
from ghost_healer.utils.stack_parser import parse_stack_trace

logger = logging.getLogger("GhostPlaywright")


# ── Page Level Patching ───────────────────────────────────────────────────────

def _heal_and_retry_page(page: Page, selector: str, action: str, original_fn, *args, **kwargs):
    try:
        return original_fn(selector, *args, **kwargs)
    except Exception as original_error:
        start = time.time()
        logger.warning(f"[GHOST] {action} failed for '{selector}'. Requesting AI heal...")
        healed, confidence = ghost_engine.get_healed_locator(selector, action, page.content(), url=page.url, framework="playwright-python")
        duration = (time.time() - start) * 1000

        if healed:
            logger.info(f"[GHOST] Healed '{selector}' → '{healed}' (action={action})")
            filename, lineno = parse_stack_trace()
            reporter.log_healing(
                original=selector,
                healed=healed,
                confidence=confidence,
                duration_ms=duration,
                action=action,
                patched_file=filename,
                framework="playwright-python",
                page_url=page.url,
                line=lineno
            )

            return original_fn(healed, *args, **kwargs)

        logger.error(f"[GHOST] Could not heal '{selector}'. Raising original error.")
        raise original_error


def _make_selector_patch(page: Page, method_name: str, action: str):
    original_fn = getattr(page, method_name)
    def patched(self, selector, *args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 2000
        return _heal_and_retry_page(page, selector, action, original_fn, *args, **kwargs)
    return types.MethodType(patched, page)


# ── Locator Level Patching ────────────────────────────────────────────────────

def _heal_and_retry_locator(locator: Locator, selector: str, page: Page, action: str, original_fn, *args, **kwargs):
    try:
        return original_fn(*args, **kwargs)
    except Exception as original_error:
        start = time.time()
        logger.warning(f"[GHOST] {action} failed for locator '{selector}'. Requesting AI heal...")
        healed, confidence = ghost_engine.get_healed_locator(selector, action, page.content(), url=page.url, framework="playwright-python")
        duration = (time.time() - start) * 1000

        if healed:
            logger.info(f"[GHOST] Healed locator '{selector}' → '{healed}' (action={action})")
            filename, lineno = parse_stack_trace()
            reporter.log_healing(
                original=selector,
                healed=healed,
                confidence=confidence,
                duration_ms=duration,
                action=action,
                patched_file=filename,
                framework="playwright-python",
                page_url=page.url,
                line=lineno
            )

            # Re-locate with healed selector
            healed_locator = page.locator(healed)
            healed_fn = getattr(healed_locator, original_fn.__name__)
            return healed_fn(*args, **kwargs)

        logger.error(f"[GHOST] Could not heal locator '{selector}'. Raising original error.")
        raise original_error

def _make_locator_patch(locator: Locator, method_name: str, action: str, selector: str, page: Page):
    original_fn = getattr(locator, method_name)
    def patched(*args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 2000
        return _heal_and_retry_locator(locator, selector, page, action, original_fn, *args, **kwargs)
    return patched

def protect_locator(locator: Locator, selector: str, page: Page) -> Locator:
    actions_to_patch = {
        "click":             "click",
        "fill":              "fill",
        "hover":             "hover",
        "check":             "check",
        "uncheck":           "uncheck",
        "dblclick":          "click",
        "press":             "press",
        "select_option":     "select",
        "wait_for":          "wait",
    }
    for method_name, action_type in actions_to_patch.items():
        if hasattr(locator, method_name):
            setattr(locator, method_name, _make_locator_patch(locator, method_name, action_type, selector, page))
    return locator


# ── Main entry point ──────────────────────────────────────────────────────────

def protect_page(page: Page) -> Page:
    # 1. Patch Page Methods
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

    # 2. Patch page.locator to return a protected Locator
    original_locator = page.locator
    def patched_locator_wrapper(self, selector, *args, **kwargs):
        loc = original_locator(selector, *args, **kwargs)
        return protect_locator(loc, selector, page)
    
    page.locator = types.MethodType(patched_locator_wrapper, page)

    logger.info("[GHOST] Page & Locator protection active. AI healing enabled for all actions.")
    return page
