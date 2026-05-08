"""
SafeLocator — core healing wrapper around Playwright locators.

Usage:
    safe = SafeLocator(page, mcp_server_url="http://localhost:8000")
    locator, heal_result = safe.locate("#old-btn", hints={"text": "Login", "tag": "button"})
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import httpx
from playwright.sync_api import Locator, Page, TimeoutError as PWTimeoutError

logger = logging.getLogger("safe_locator")

MCP_SERVER_URL = "http://localhost:8000"
LOCATE_TIMEOUT_MS = 3_000  # Time before we try healing


@dataclass
class HealResult:
    """Structured result of a healing attempt."""
    original_locator: str
    healed_locator: Optional[str]
    confidence_score: float
    confidence_level: str          # LOW | MEDIUM | HIGH
    decision: str                  # AUTO_HEAL | MANUAL_REVIEW | FAIL
    was_healed: bool
    healing_id: str
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    candidates_count: int = 0
    reasoning: str = ""


class SafeLocator:
    """
    Wrapper around Playwright page that adds self-healing capability.
    On locator failure, contacts the MCP server to get a healed locator.
    """

    def __init__(self, page: Page, mcp_server_url: str = MCP_SERVER_URL):
        self.page = page
        self.mcp_server_url = mcp_server_url.rstrip("/")

    def locate(
        self,
        selector: str,
        action: str = "click",
        hints: Optional[Dict[str, Any]] = None,
        test_name: Optional[str] = None,
    ) -> Tuple[Locator, Optional[HealResult]]:
        """
        Attempt to locate an element. On failure, request healing from MCP server.

        Returns:
            (Locator, HealResult | None)
            HealResult is None if the original locator worked fine.

        Raises:
            Exception if healing fails (decision=FAIL or no healed locator returned).
        """
        # ── Try original locator first ────────────────────────────────────
        err_msg = ""
        try:
            locator = self.page.locator(selector)
            locator.wait_for(state="attached", timeout=LOCATE_TIMEOUT_MS)
            logger.debug(f"Locator OK: '{selector}'")
            return locator, None

        except (PWTimeoutError, Exception) as err:
            err_msg = str(err)
            logger.warning(f"Locator FAILED: '{selector}' — {err_msg}")
            logger.info(f"Requesting healing from MCP server for '{selector}'")

        # ── Capture DOM snapshot ──────────────────────────────────────────
        dom_snapshot = self.page.content()

        # ── Request healing ───────────────────────────────────────────────
        heal_result = self._request_healing(
            selector=selector,
            dom_snapshot=dom_snapshot,
            failure_reason=err_msg,
            page_url=self.page.url,
            action=action,
            hints=hints,
            test_name=test_name,
        )

        logger.info(
            f"Heal result | decision={heal_result.decision} | "
            f"score={heal_result.confidence_score:.1f} | "
            f"healed={heal_result.healed_locator}"
        )

        if heal_result.decision == "FAIL" or not heal_result.healed_locator:
            raise Exception(
                f"Self-healing FAILED for '{selector}'. "
                f"Score={heal_result.confidence_score:.1f}. {heal_result.reasoning}"
            )

        healed_locator = self.page.locator(heal_result.healed_locator)
        return healed_locator, heal_result

    def _request_healing(
        self,
        selector: str,
        dom_snapshot: str,
        failure_reason: str,
        page_url: str,
        action: str,
        hints: Optional[Dict[str, Any]],
        test_name: Optional[str],
    ) -> HealResult:
        payload = {
            "original_locator": selector,
            "dom_snapshot": dom_snapshot,
            "failure_reason": failure_reason,
            "page_url": page_url,
            "action": action,
            "test_name": test_name,
            "element_hints": hints,
        }
        try:
            response = httpx.post(
                f"{self.mcp_server_url}/api/heal-locator",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error(f"MCP server request failed: {e}")
            return HealResult(
                original_locator=selector,
                healed_locator=None,
                confidence_score=0.0,
                confidence_level="LOW",
                decision="FAIL",
                was_healed=False,
                healing_id="unknown",
                reasoning=f"MCP server unreachable: {e}",
            )

        return HealResult(
            original_locator=selector,
            healed_locator=data.get("healed_locator"),
            confidence_score=data.get("confidence_score", 0.0),
            confidence_level=data.get("confidence_level", "LOW"),
            decision=data.get("decision", "FAIL"),
            was_healed=data.get("decision") == "AUTO_HEAL",
            healing_id=data.get("healing_id", ""),
            score_breakdown=data.get("execution_trace", {}).get("all_candidates", [{}])[0].get("breakdown", {}),
            candidates_count=len(data.get("candidates", [])),
            reasoning=data.get("execution_trace", {}).get("steps", [{}])[-1].get("detail", ""),
        )
