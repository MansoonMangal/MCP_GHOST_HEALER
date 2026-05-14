import types
import time
from playwright.sync_api import Page
from ghost_healer.core.engine import ghost_engine
from ghost_healer.utils.reporter import reporter

def protect_page(page: Page):
    """
    [GHOST] Patches a Playwright Page instance with AI Self-Healing and Reporting.
    """
    original_fill = page.fill
    def patched_fill(self, selector, value, **kwargs):
        try:
            return original_fill(selector, value, timeout=2000, **kwargs)
        except Exception:
            start = time.time()
            healed = ghost_engine.get_healed_locator(selector, "fill", page.content())
            duration = (time.time() - start) * 1000
            
            if healed:
                # Log to reporter
                reporter.log_healing(selector, healed, 0.95, duration) 
                return original_fill(healed, value, **kwargs)
            raise

    original_click = page.click
    def patched_click(self, selector, **kwargs):
        try:
            return original_click(selector, timeout=2000, **kwargs)
        except Exception:
            start = time.time()
            healed = ghost_engine.get_healed_locator(selector, "click", page.content())
            duration = (time.time() - start) * 1000

            if healed:
                # Log to reporter
                reporter.log_healing(selector, healed, 0.95, duration)
                return original_click(healed, **kwargs)
            raise

    # Apply patches
    page.fill = types.MethodType(patched_fill, page)
    page.click = types.MethodType(patched_click, page)
    return page
