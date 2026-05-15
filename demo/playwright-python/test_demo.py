"""
👻 Ghost Healer Demo — Playwright Python (ZERO code changes)

This test file contains ZERO Ghost Healer code.
No imports. No fixtures. No wrappers.

Ghost Healer activates automatically because:
  pip install ghost-healer
  → registers pytest plugin via entry_points
  → plugin auto-wraps the `page` fixture for every test

The locators below are intentionally WRONG.
Ghost Healer heals them. Test passes. You changed nothing.

Run:
    pytest demo/playwright-python/test_demo.py -v -s
"""
# ← NO ghost_healer import
# ← NO protect_page() call
# ← NO fixtures


def test_login_with_broken_locators(page):
    """
    Standard Playwright test — no Ghost Healer code at all.
    Locators are broken. Ghost Healer heals them automatically.
    """
    page.goto("https://www.saucedemo.com/")

    # Standard page.fill() — broken selector, Ghost heals it
    page.fill("#user-name-WRONG", "standard_user")

    # Standard page.fill() — broken selector, Ghost heals it
    page.fill("#password-WRONG", "secret_sauce")

    # Standard page.click() — broken selector, Ghost heals it
    page.click("#login-btn-WRONG")

    assert page.url == "https://www.saucedemo.com/inventory.html"
    print("\n✅ Test passed — standard Playwright code, zero Ghost Healer imports!")
