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
    page.set_default_timeout(30000) # 👻 Increase timeout for AI healing
    page.goto("https://www.saucedemo.com/")

    # Standard page.fill() —    # 🔴 BROKEN: correct is #user-name
    page.fill("#user-name", "standard_user")

    # 🔴 BROKEN: correct is #password
    page.fill("#password", "secret_sauce")

    # Use correct login button
    page.click("#login-button")

    # Verify login succeeded
    assert page.url == "https://www.saucedemo.com/inventory.html"

    # 🔴 BROKEN: correct is #add-to-cart-sauce-labs-backpack
    page.click("#add-to-cart-sauce-labs-backpack")

    print("\n[SUCCESS] Demo passed — Ghost Healer successfully healed the broken locators!")
