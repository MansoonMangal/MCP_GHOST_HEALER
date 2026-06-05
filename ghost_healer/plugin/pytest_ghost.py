"""
Ghost Healer — Pytest Plugin (absolute zero-change activation).

Playwright: auto-wraps `page` fixture when pytest-playwright is used.
Selenium: auto-discovers common driver fixture names from ghost.yaml.
"""
import logging
import pytest

logger = logging.getLogger("GhostPlugin")

COMMON_SELENIUM_FIXTURES = ("driver", "browser", "webdriver", "selenium_driver")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "ghost: Mark a test to use Ghost Healer AI self-healing.",
    )
    # Reload settings after .env is available (zero-change: only pip install + .env key)
    try:
        from ghost_healer.core import config as cfg_module
        cfg_module.settings = cfg_module.load_config()
    except Exception:
        pass


def _selenium_fixture_names(request) -> list:
    try:
        from ghost_healer.core.config import settings
        names = list(settings.healing.selenium_fixture_names or [])
        legacy = getattr(settings.healing, "selenium_fixture_name", None)
        if legacy and legacy not in names:
            names.insert(0, legacy)
        return names or list(COMMON_SELENIUM_FIXTURES)
    except Exception:
        return list(COMMON_SELENIUM_FIXTURES)


@pytest.fixture(autouse=True)
def _ghost_playwright_heal(request):
    if "page" not in request.fixturenames:
        return
    page = request.getfixturevalue("page")
    try:
        from ghost_healer.adapters.playwright import protect_page
        protect_page(page)
        logger.debug("[GHOST-PLUGIN] Playwright page auto-protected.")
    except Exception as e:
        logger.warning(f"[GHOST-PLUGIN] Could not protect Playwright page: {e}")


@pytest.fixture(autouse=True)
def _ghost_selenium_heal(request):
    for fixture_name in _selenium_fixture_names(request):
        if fixture_name not in request.fixturenames:
            continue
        try:
            driver = request.getfixturevalue(fixture_name)
        except Exception:
            continue
        if driver is None:
            continue
        try:
            from ghost_healer.adapters.selenium import protect_driver
            protect_driver(driver)
            logger.debug(f"[GHOST-PLUGIN] Selenium '{fixture_name}' auto-protected.")
            return
        except Exception as e:
            logger.warning(f"[GHOST-PLUGIN] Could not protect Selenium driver: {e}")
