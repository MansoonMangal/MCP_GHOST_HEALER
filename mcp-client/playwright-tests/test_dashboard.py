"""
test_dashboard.py — Self-Healing Demo: Dashboard Page

Tests dashboard interactive elements with intentionally broken selectors
to demonstrate healing on data-heavy pages.
"""
import logging
import pytest
from playwright.sync_api import Page, expect

from wrappers.safe_click import safe_click
from test_runner.healing_reporter import HealingEvent, attach_healing_event

logger = logging.getLogger("test_dashboard")

BROKEN_DASHBOARD_URL = "http://localhost:3000/broken-version/dashboard.html"
MCP_URL = "http://localhost:8000"


class TestDashboardSelfHealing:

    def test_logout_button_heals(self, page: Page, request):
        """
        Scenario: logout button class changed from .logout-btn → .btn-signout
        """
        logger.info("=" * 60)
        logger.info("TEST: test_logout_button_heals")

        page.goto(BROKEN_DASHBOARD_URL)
        page.wait_for_load_state("domcontentloaded")

        result = safe_click(
            page=page,
            selector=".logout-btn",     # OLD selector
            hints={"text": "Logout", "tag": "button"},
            test_name="test_logout_button_heals",
            mcp_server_url=MCP_URL,
        )

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            logger.info(f"   Score: {result.confidence_score:.1f} | Level: {result.confidence_level}")
            attach_healing_event(request, HealingEvent(
                test_name="test_logout_button_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))

    def test_add_user_button_heals(self, page: Page, request):
        """
        Scenario: add-user button ID changed from #add-user → #new-user-btn
        """
        logger.info("=" * 60)
        logger.info("TEST: test_add_user_button_heals")

        page.goto(BROKEN_DASHBOARD_URL)
        page.wait_for_load_state("domcontentloaded")

        result = safe_click(
            page=page,
            selector="#add-user",        # OLD selector
            hints={"text": "Add User", "tag": "button"},
            test_name="test_add_user_button_heals",
            mcp_server_url=MCP_URL,
        )

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            attach_healing_event(request, HealingEvent(
                test_name="test_add_user_button_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))

    def test_reports_link_heals(self, page: Page, request):
        """
        Scenario: nav link aria-label changed
        """
        logger.info("=" * 60)
        logger.info("TEST: test_reports_link_heals")

        page.goto(BROKEN_DASHBOARD_URL)
        page.wait_for_load_state("domcontentloaded")

        result = safe_click(
            page=page,
            selector='[aria-label="Reports"]',   # OLD selector
            hints={"text": "Reports", "tag": "a"},
            test_name="test_reports_link_heals",
            mcp_server_url=MCP_URL,
        )

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            attach_healing_event(request, HealingEvent(
                test_name="test_reports_link_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))
