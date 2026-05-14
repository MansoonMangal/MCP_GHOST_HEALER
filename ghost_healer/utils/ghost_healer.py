import logging
from playwright.sync_api import Page, Locator
from ghost_framework.wrappers.base_wrapper import execute_safe_action

logger = logging.getLogger("GhostHealer")

def apply_ghost_mode_to_instance(page: Page):
    """
    [GHOST] GHOST MODE v3: 
    Patches a SPECIFIC instance of Page.
    """
    print(f"[GHOST] Protecting instance: {page}")
    
    # Patch the instance methods
    original_fill = page.fill
    def patched_fill(self, selector, value, **kwargs):
        try:
            # Try original with short timeout to trigger healing faster
            return original_fill(selector, value, timeout=2000, **kwargs)
        except Exception:
            print(f"[GHOST] Intercepted Failure: fill('{selector}')")
            return execute_safe_action(page, selector, "fill", lambda loc: loc.fill(value, **kwargs))
            
    original_click = page.click
    def patched_click(self, selector, **kwargs):
        try:
            # Try original with short timeout to trigger healing faster
            return original_click(selector, timeout=2000, **kwargs)
        except Exception:
            print(f"[GHOST] Intercepted Failure: click('{selector}')")
            return execute_safe_action(page, selector, "click", lambda loc: loc.click(**kwargs))

    # Apply to instance
    import types
    page.fill = types.MethodType(patched_fill, page)
    page.click = types.MethodType(patched_click, page)
    print("[OK] Instance protected!")
