"""
safe_click — self-healing wrapper for Playwright click actions.

Usage:
    from wrappers.safe_click import safe_click

    heal_result = safe_click(page, "#login-btn", hints={"text": "Login", "tag": "button"})
"""
import logging
from typing import Any, Dict, Optional

from playwright.sync_api import Page

from wrappers.safe_locator import HealResult, SafeLocator

logger = logging.getLogger("safe_click")


def safe_click(
    page: Page,
    selector: str,
    hints: Optional[Dict[str, Any]] = None,
    test_name: Optional[str] = None,
    mcp_server_url: str = "http://localhost:8000",
    **click_kwargs,
) -> Optional[HealResult]:
    """
    Attempt to click an element. If the locator fails, the MCP server is
    contacted to find the best healed locator. Retries once with healed locator.

    Args:
        page:           Playwright Page object
        selector:       Original CSS/XPath/Playwright selector
        hints:          Optional known element features {text, tag, type, ...}
        test_name:      Test identifier for traceability
        mcp_server_url: MCP server base URL
        **click_kwargs: Extra kwargs forwarded to Playwright's .click()

    Returns:
        HealResult if healing occurred, None if original locator worked.

    Raises:
        Exception if healing decision is FAIL.
    """
    safe = SafeLocator(page, mcp_server_url=mcp_server_url)
    locator, heal_result = safe.locate(selector, action="click", hints=hints, test_name=test_name)

    if heal_result:
        logger.info(
            f"[safe_click] Healed click | '{selector}' → '{heal_result.healed_locator}' | "
            f"score={heal_result.confidence_score:.1f} | level={heal_result.confidence_level}"
        )
    else:
        logger.debug(f"[safe_click] Direct click on '{selector}'")

    locator.click(**click_kwargs)
    return heal_result
