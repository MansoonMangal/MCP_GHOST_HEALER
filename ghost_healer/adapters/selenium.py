"""
Ghost Healer — Selenium Python Adapter

Patches a Selenium WebDriver and WebElement instances with AI Self-Healing.
"""
import time
import logging
import types
from typing import Any

from ghost_healer.core.engine import ghost_engine
from ghost_healer.utils.reporter import reporter
from ghost_healer.utils.stack_parser import parse_stack_trace

logger = logging.getLogger("GhostSelenium")


def _get_css_selector(by: Any, value: str) -> str:
    from selenium.webdriver.common.by import By
    mapping = {
        By.ID:         f"#{value}",
        By.CLASS_NAME: f".{value}",
        By.NAME:       f"[name='{value}']",
        By.TAG_NAME:   value,
        By.CSS_SELECTOR: value,
        By.XPATH:      value,
        By.LINK_TEXT:  f"text={value}",
        By.PARTIAL_LINK_TEXT: f"text={value}",
    }
    return mapping.get(by, value)


def _get_dom(drv) -> str:
    try:
        return drv.execute_script("return document.documentElement.outerHTML")
    except Exception:
        try:
            return drv.page_source
        except Exception:
            return ""

# ── WebElement Level Patching ─────────────────────────────────────────────────

def _heal_and_retry_element(element: Any, driver: Any, selector: str, action: str, original_fn, *args, **kwargs):
    try:
        return original_fn(*args, **kwargs)
    except Exception as original_error:
        start = time.time()
        logger.warning(f"[GHOST] {action} failed on element '{selector}'. Requesting AI heal...")

        dom = _get_dom(driver)
        url = driver.current_url
        healed, confidence = ghost_engine.get_healed_locator(selector, action, dom, url=url, framework="selenium-python")
        duration = (time.time() - start) * 1000

        if healed:
            logger.info(f"[GHOST] Healed element '{selector}' → '{healed}' (action={action})")
            filename, lineno = parse_stack_trace()
            reporter.log_healing(
                original=selector,
                healed=healed,
                confidence=confidence,
                duration_ms=duration,
                action=action,
                patched_file=filename,
                framework="selenium-python"
            )

            from selenium.webdriver.common.by import By
            # Find the new element
            new_element = driver.find_element(By.CSS_SELECTOR, healed)
            # Re-run the action on the new element
            new_fn = getattr(new_element, original_fn.__name__)
            return new_fn(*args, **kwargs)

        logger.error(f"[GHOST] Could not heal '{selector}'. Raising original error.")
        raise original_error

def _make_element_patch(element: Any, driver: Any, method_name: str, action: str, selector: str):
    original_fn = getattr(element, method_name)
    def patched(*args, **kwargs):
        return _heal_and_retry_element(element, driver, selector, action, original_fn, *args, **kwargs)
    return patched

def protect_element(element: Any, driver: Any, selector: str) -> Any:
    actions_to_patch = {
        "click":     "click",
        "send_keys": "send_keys",
        "clear":     "clear",
        "submit":    "submit",
    }
    for method_name, action_type in actions_to_patch.items():
        if hasattr(element, method_name):
            setattr(element, method_name, _make_element_patch(element, driver, method_name, action_type, selector))
    return element


# ── WebDriver Level Patching ──────────────────────────────────────────────────

def protect_driver(driver: Any) -> Any:
    original_find_element = driver.find_element
    original_find_elements = driver.find_elements

    def healed_find_element(by: Any, value: str):
        selector = _get_css_selector(by, value)
        try:
            element = original_find_element(by, value)
            return protect_element(element, driver, selector)
        except Exception as original_error:
            try:
                from selenium.common.exceptions import NoSuchElementException
                if not isinstance(original_error, NoSuchElementException):
                    raise original_error
            except ImportError:
                raise original_error

            logger.warning(f"[GHOST] find_element failed for '{selector}'. Requesting AI heal...")

            start = time.time()
            dom = _get_dom(driver)
            url = driver.current_url
            healed, confidence = ghost_engine.get_healed_locator(selector, "find", dom, url=url, framework="selenium-python")
            duration = (time.time() - start) * 1000

            if healed:
                logger.info(f"[GHOST] Healed '{selector}' → '{healed}'")
                filename, lineno = parse_stack_trace()
                reporter.log_healing(
                    original=selector,
                    healed=healed,
                    confidence=confidence,
                    duration_ms=duration,
                    action="find",
                    patched_file=filename,
                    framework="selenium-python"
                )

                from selenium.webdriver.common.by import By
                element = original_find_element(By.CSS_SELECTOR, healed)
                return protect_element(element, driver, healed)

            logger.error(f"[GHOST] Could not heal '{selector}'. Raising original error.")
            raise original_error

    def healed_find_elements(by: Any, value: str):
        selector = _get_css_selector(by, value)
        try:
            elements = original_find_elements(by, value)
            if elements:
                return [protect_element(e, driver, selector) for e in elements]
            raise Exception("No elements found")
        except Exception as original_error:
            logger.warning(f"[GHOST] find_elements empty for '{selector}'. Requesting AI heal...")

            start = time.time()
            dom = _get_dom(driver)
            url = driver.current_url
            healed, confidence = ghost_engine.get_healed_locator(selector, "find", dom, url=url, framework="selenium-python")
            duration = (time.time() - start) * 1000

            if healed:
                logger.info(f"[GHOST] Healed '{selector}' → '{healed}'")
                filename, lineno = parse_stack_trace()
                reporter.log_healing(
                    original=selector,
                    healed=healed,
                    confidence=confidence,
                    duration_ms=duration,
                    action="find",
                    patched_file=filename,
                    framework="selenium-python"
                )
                from selenium.webdriver.common.by import By
                elements = original_find_elements(By.CSS_SELECTOR, healed)
                return [protect_element(e, driver, healed) for e in elements]

            raise original_error

    driver.find_element = healed_find_element
    driver.find_elements = healed_find_elements

    logger.info("[GHOST] Selenium driver & element protection active. AI healing enabled.")
    return driver
