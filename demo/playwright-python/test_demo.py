"""
👻 Ghost Healer Demo — Playwright Python

This demo intentionally uses BROKEN locators on SauceDemo.
Ghost Healer intercepts each failure, heals the locator via the AI Brain,
and the test passes without any manual fix.

Run:
    pytest demo/playwright-python/test_demo.py -v -s
"""
import pytest
from ghost_healer import protect_page


@pytest.fixture(autouse=True)
def ghost_mode(page):
    """Activate Ghost Healer on every test."""
    protect_page(page)
    yield


def test_login_with_broken_locators(page):
    """
    BROKEN LOCATORS used intentionally:
      #user-name-WRONG → should be #user-name
      #password-WRONG  → should be #password
      #login-btn-WRONG → should be #login-button

    Ghost Healer will intercept each failure and heal silently.
    The test will PASS despite all three broken locators.
    """
    page.goto("https://www.saucedemo.com/")

    # 🔴 BROKEN: correct is #user-name
    page.fill("#user-name-WRONG", "standard_user")

    # 🔴 BROKEN: correct is #password
    page.fill("#password-WRONG", "secret_sauce")

    # 🔴 BROKEN: correct is #login-button
    page.click("#login-btn-WRONG")

    # Verify login succeeded
    assert page.url == "https://www.saucedemo.com/inventory.html"
    print("\n✅ Login succeeded despite all broken locators — Ghost Healer worked!")
