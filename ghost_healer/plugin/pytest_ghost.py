"""
Ghost Healer — Pytest Plugin (Auto Interception)

Automatically injects AI self-healing into ALL Playwright tests
without requiring any user code change.

How it works:
  - Hooks into pytest-playwright's `page` fixture
  - Calls protect_page() automatically after each page is created
  - Zero configuration needed — just install ghost-healer

Activation:
  This plugin is auto-discovered by pytest via the `entry_points` in pyproject.toml:
    [project.entry-points."pytest11"]
    ghost = "ghost_healer.plugin.pytest_ghost"

Usage:
  Just install and run — no conftest.py changes needed:
    pip install ghost-healer
    pytest
"""
import logging
import pytest

logger = logging.getLogger("GhostPlugin")


def pytest_configure(config: pytest.Config) -> None:
    """Register the Ghost Healer plugin."""
    config.addinivalue_line(
        "markers",
        "ghost: Mark a test to use Ghost Healer AI self-healing (auto-applied to all tests)."
    )


@pytest.fixture(autouse=True)
def _ghost_auto_heal(page):
    """
    Auto-injected fixture that wraps every Playwright `page` with Ghost protection.

    This fixture runs automatically for every test that uses the `page` fixture
    from pytest-playwright. No user code change required.
    """
    try:
        from ghost_healer.adapters.playwright import protect_page
        protect_page(page)
        logger.debug("[GHOST-PLUGIN] Auto-protection active for this test.")
    except ImportError:
        logger.warning("[GHOST-PLUGIN] playwright adapter not available. Skipping.")
    except Exception as e:
        logger.warning(f"[GHOST-PLUGIN] Could not protect page: {e}")

    yield


@pytest.fixture(autouse=True)
def _ghost_driver_heal(request):
    """
    Auto-injected fixture for Selenium WebDriver tests.
    Looks for a `driver` fixture and patches it automatically.
    """
    driver = request.node.funcargs.get("driver")
    if driver is None:
        return

    try:
        from ghost_healer.adapters.selenium import protect_driver
        protect_driver(driver)
        logger.debug("[GHOST-PLUGIN] Auto-protection active for Selenium driver.")
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"[GHOST-PLUGIN] Could not protect driver: {e}")
