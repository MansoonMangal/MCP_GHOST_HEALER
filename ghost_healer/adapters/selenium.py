"""
Ghost Healer — Selenium Python Adapter

Patches a Selenium WebDriver instance with AI Self-Healing.
Works identically to the Playwright adapter — invisible to the test author.

Usage:
    from ghost_healer.adapters.selenium import protect_driver
    from selenium import webdriver

    driver = webdriver.Chrome()
    protect_driver(driver)  # 👻 Ghost Mode Active

    # Now all find_element calls are self-healing
    driver.find_element(By.ID, "login-btn").click()
"""
import time
import logging
from typing import Any

from ghost_healer.core.engine import ghost_engine
from ghost_healer.utils.reporter import reporter

logger = logging.getLogger("GhostSelenium")

# Selenium action mappings
_SELENIUM_ACTION = "click"


def _get_css_selector(by: Any, value: str) -> str:
    """Convert Selenium By strategy + value to a CSS selector string for the AI Brain."""
    from selenium.webdriver.common.by import By
    mapping = {
        By.ID:         f"#{value}",
        By.CLASS_NAME: f".{value}",
        By.NAME:       f"[name='{value}']",
        By.TAG_NAME:   value,
        By.CSS_SELECTOR: value,
        By.XPATH:      value,          # Brain supports XPath strings
        By.LINK_TEXT:  f"text={value}",
        By.PARTIAL_LINK_TEXT: f"text={value}",
    }
    return mapping.get(by, value)


def protect_driver(driver: Any) -> Any:
    """
    👻 Patches a Selenium WebDriver with AI Self-Healing.

    Wraps:
      - find_element       → heals broken locators on NoSuchElementException
      - find_elements      → same healing logic for multi-element queries

    Returns the same driver instance (patched in-place).
    """
    original_find_element = driver.find_element
    original_find_elements = driver.find_elements

    def _get_dom(drv) -> str:
        """Capture current page source as DOM snapshot."""
        try:
            return drv.page_source
        except Exception:
            return ""

    def healed_find_element(by: Any, value: str):
        try:
            return original_find_element(by, value)
        except Exception as original_error:
            try:
                from selenium.common.exceptions import NoSuchElementException
                if not isinstance(original_error, NoSuchElementException):
                    raise original_error
            except ImportError:
                raise original_error

            selector = _get_css_selector(by, value)
            logger.warning(f"[GHOST] find_element failed for '{selector}'. Requesting AI heal...")

            start = time.time()
            dom = _get_dom(driver)
            healed = ghost_engine.get_healed_locator(selector, "click", dom)
            duration = (time.time() - start) * 1000

            if healed:
                logger.info(f"[GHOST] Healed '{selector}' → '{healed}'")
                reporter.log_healing(selector, healed, 0.0, duration)
                from selenium.webdriver.common.by import By
                return original_find_element(By.CSS_SELECTOR, healed)

            logger.error(f"[GHOST] Could not heal '{selector}'. Raising original error.")
            raise original_error

    def healed_find_elements(by: Any, value: str):
        try:
            elements = original_find_elements(by, value)
            if elements:
                return elements
            # If empty list (not an exception), try to heal
            raise Exception("No elements found")
        except Exception as original_error:
            selector = _get_css_selector(by, value)
            logger.warning(f"[GHOST] find_elements empty for '{selector}'. Requesting AI heal...")

            start = time.time()
            dom = _get_dom(driver)
            healed = ghost_engine.get_healed_locator(selector, "click", dom)
            duration = (time.time() - start) * 1000

            if healed:
                logger.info(f"[GHOST] Healed '{selector}' → '{healed}'")
                reporter.log_healing(selector, healed, 0.0, duration)
                from selenium.webdriver.common.by import By
                return original_find_elements(By.CSS_SELECTOR, healed)

            raise original_error

    # Apply patches
    driver.find_element = healed_find_element
    driver.find_elements = healed_find_elements

    logger.info("[GHOST] Selenium driver protection active. AI healing enabled.")
    return driver
