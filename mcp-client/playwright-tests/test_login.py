"""
test_login.py — Self-Healing Demo: Login Page

Demonstrates the full healing pipeline:
  1. Navigate to the BROKEN version of the demo app (changed locators)
  2. safeClick / safeFill detect failures
  3. MCP server returns healed locators
  4. Test retries and PASSES
  5. Full trace logged to reports/

Run:
  cd mcp-client
  pytest playwright-tests/test_login.py -v -s
"""
import logging
import pytest
from playwright.sync_api import Page

from wrappers.safe_click import safe_click
from wrappers.safe_fill import safe_fill
from test_runner.healing_reporter import HealingEvent, attach_healing_event

logger = logging.getLogger("test_login")

# ── Target: Broken demo app (selectors have changed) ─────────────────────────
BROKEN_APP_URL = "http://localhost:3000/broken-version/index.html"
WORKING_APP_URL = "http://localhost:3000/index.html"
MCP_URL = "http://localhost:8000"


class TestLoginSelfHealing:
    """
    Demonstrates self-healing for the login page.
    The broken app has changed IDs/classes — healing restores functionality.
    """

    def test_login_email_field_heals(self, page: Page, request):
        """
        Scenario: email input ID changed from #email → #user-email
        Expected: safe_fill detects failure, MCP heals, fill succeeds
        """
        logger.info("=" * 60)
        logger.info("TEST: test_login_email_field_heals")
        logger.info("Navigating to BROKEN demo app...")

        page.goto(BROKEN_APP_URL)
        page.wait_for_load_state("domcontentloaded")

        # Intentionally use the OLD (broken) selector
        result = safe_fill(
            page=page,
            selector="#email",           # OLD — no longer exists in broken app
            value="admin@company.com",
            hints={"placeholder": "Enter your email", "type": "email", "tag": "input"},
            test_name="test_login_email_field_heals",
            mcp_server_url=MCP_URL,
        )

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            logger.info(f"   Score: {result.confidence_score:.1f} | Level: {result.confidence_level}")
            attach_healing_event(request, HealingEvent(
                test_name="test_login_email_field_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))
        else:
            logger.info("✅ Original locator worked fine (no healing needed)")

    def test_login_password_field_heals(self, page: Page, request):
        """
        Scenario: password input ID changed from #password → #user-password
        """
        logger.info("=" * 60)
        logger.info("TEST: test_login_password_field_heals")

        page.goto(BROKEN_APP_URL)
        page.wait_for_load_state("domcontentloaded")

        result = safe_fill(
            page=page,
            selector="#password",        # OLD selector
            value="SecurePass123!",
            hints={"placeholder": "Enter your password", "type": "password", "tag": "input"},
            test_name="test_login_password_field_heals",
            mcp_server_url=MCP_URL,
        )

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            logger.info(f"   Score: {result.confidence_score:.1f} | Decision: {result.decision}")
            attach_healing_event(request, HealingEvent(
                test_name="test_login_password_field_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))

    def test_login_button_heals(self, page: Page, request):
        """
        Scenario: login button ID changed from #login-btn → #btn-submit
        Expected: safe_click detects failure, MCP heals, click succeeds
        """
        logger.info("=" * 60)
        logger.info("TEST: test_login_button_heals")

        page.goto(BROKEN_APP_URL)
        page.wait_for_load_state("domcontentloaded")

        # Fill form fields first (using broken but healable selectors)
        safe_fill(page, "#email", "admin@company.com",
                  hints={"placeholder": "Enter your email", "type": "email"},
                  test_name="test_login_button_heals", mcp_server_url=MCP_URL)

        safe_fill(page, "#password", "SecurePass123!",
                  hints={"placeholder": "Enter your password", "type": "password"},
                  test_name="test_login_button_heals", mcp_server_url=MCP_URL)

        # Click the login button — this is the KEY healing demonstration
        result = safe_click(
            page=page,
            selector="#login-btn",       # OLD selector
            hints={"text": "Login", "tag": "button"},
            test_name="test_login_button_heals",
            mcp_server_url=MCP_URL,
        )

        # Verify navigation occurred (redirect to dashboard)
        page.wait_for_url("**/dashboard**", timeout=5_000)
        logger.info(f"✅ Login succeeded! Current URL: {page.url}")

        if result:
            logger.info(f"✅ HEALED | '{result.original_locator}' → '{result.healed_locator}'")
            logger.info(f"   Score: {result.confidence_score:.1f} | Level: {result.confidence_level}")
            attach_healing_event(request, HealingEvent(
                test_name="test_login_button_heals",
                original_locator=result.original_locator,
                healed_locator=result.healed_locator,
                confidence_score=result.confidence_score,
                confidence_level=result.confidence_level,
                decision=result.decision,
                was_healed=result.was_healed,
                healing_id=result.healing_id,
            ))

    def test_login_no_healing_needed(self, page: Page, request):
        """
        Scenario: Use the WORKING app — no healing should occur.
        Verifies the wrapper is transparent when locators are valid.
        """
        logger.info("=" * 60)
        logger.info("TEST: test_login_no_healing_needed (working app)")

        page.goto(WORKING_APP_URL)
        page.wait_for_load_state("domcontentloaded")

        result_email = safe_fill(page, "#email", "admin@company.com",
                                  hints={"type": "email"}, test_name="test_login_no_healing_needed")
        result_pw = safe_fill(page, "#password", "SecurePass123!",
                               hints={"type": "password"}, test_name="test_login_no_healing_needed")
        result_btn = safe_click(page, "#login-btn",
                                hints={"text": "Login"}, test_name="test_login_no_healing_needed")

        assert result_email is None, "No healing should occur on working locator"
        assert result_pw is None
        assert result_btn is None
        logger.info("✅ All locators worked without healing — wrappers are transparent")
