"""
safe_fill — self-healing wrapper for Playwright fill/type actions.

Usage:
    from wrappers.safe_fill import safe_fill

    heal_result = safe_fill(page, "#email", "user@example.com",
                            hints={"placeholder": "Email", "type": "email"})
"""
import logging
from typing import Any, Dict, Optional

from playwright.sync_api import Page

from wrappers.safe_locator import HealResult, SafeLocator

logger = logging.getLogger("safe_fill")


def safe_fill(
    page: Page,
    selector: str,
    value: str,
    hints: Optional[Dict[str, Any]] = None,
    test_name: Optional[str] = None,
    mcp_server_url: str = "http://localhost:8000",
) -> Optional[HealResult]:
    """
    Attempt to fill an input element. On locator failure, contacts MCP server
    for healing and retries fill with healed locator.

    Args:
        page:           Playwright Page object
        selector:       Original selector string
        value:          Text value to fill into the input
        hints:          Known element features (placeholder, type, name, ...)
        test_name:      Test identifier for traceability
        mcp_server_url: MCP server base URL

    Returns:
        HealResult if healing occurred, None if original locator worked.

    Raises:
        Exception if healing decision is FAIL.
    """
    safe = SafeLocator(page, mcp_server_url=mcp_server_url)
    locator, heal_result = safe.locate(selector, action="fill", hints=hints, test_name=test_name)

    if heal_result:
        logger.info(
            f"[safe_fill] Healed fill | '{selector}' → '{heal_result.healed_locator}' | "
            f"score={heal_result.confidence_score:.1f}"
        )
    else:
        logger.debug(f"[safe_fill] Direct fill on '{selector}'")

    locator.fill(value)
    return heal_result
