"""
Ghost Healer — Pytest Plugin (Zero-Code Auto Interception)

Automatically injects AI self-healing into ALL tests without any
changes to test files.

==========================================================
For Playwright Python tests:
  ZERO changes needed. Just install ghost-healer.
  pytest automatically activates the page fixture wrapper.

For Selenium Python tests:
  Add ONE fixture to conftest.py:

    @pytest.fixture(autouse=True)
    def ghost_selenium(driver):
        from ghost_healer.adapters.selenium import protect_driver
        protect_driver(driver)
        yield

  Or — for truly zero changes — register your driver fixture
  name in ghost.yaml:
    healing:
      selenium_fixture_name: "driver"  # name of your driver fixture

==========================================================
Activation (automatic via pyproject.toml entry_points):
  [project.entry-points."pytest11"]
  ghost = "ghost_healer.plugin.pytest_ghost"
"""
import logging
import pytest

logger = logging.getLogger("GhostPlugin")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "ghost: Mark a test to use Ghost Healer AI self-healing."
    )


# ── Playwright auto-injection ─────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _ghost_playwright_heal(request):
    """
    Auto-inject Ghost Healer for any test using pytest-playwright's `page` fixture.
    If the test does NOT have a `page` fixture, this does nothing.
    """
    # Only activate if the test uses the `page` fixture from pytest-playwright
    if "page" not in request.fixturenames:
        return

    page = request.getfixturevalue("page")

    try:
        from ghost_healer.adapters.playwright import protect_page
        protect_page(page)
        logger.debug("[GHOST-PLUGIN] Playwright page auto-protected.")
    except Exception as e:
        logger.warning(f"[GHOST-PLUGIN] Could not protect Playwright page: {e}")


# ── Selenium auto-injection ───────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _ghost_selenium_heal(request):
    """
    Auto-inject Ghost Healer for Selenium WebDriver tests.

    Looks for a fixture named 'driver' (configurable via ghost.yaml
    healing.selenium_fixture_name). If found, wraps it automatically.
    """
    # Read the expected fixture name from config
    try:
        from ghost_healer.core.config import settings
        fixture_name = getattr(settings.healing, "selenium_fixture_name", "driver")
    except Exception:
        fixture_name = "driver"

    if fixture_name not in request.fixturenames:
        return

    driver = request.getfixturevalue(fixture_name)
    if driver is None:
        return

    try:
        from ghost_healer.adapters.selenium import protect_driver
        protect_driver(driver)
        logger.debug(f"[GHOST-PLUGIN] Selenium '{fixture_name}' auto-protected.")
    except Exception as e:
        logger.warning(f"[GHOST-PLUGIN] Could not protect Selenium driver: {e}")
