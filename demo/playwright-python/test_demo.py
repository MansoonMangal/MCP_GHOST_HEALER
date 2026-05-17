"""
👻 Ghost Healer Demo — Playwright Python Locator API Validation

PURPOSE:
This demo validates the NEW enterprise Ghost architecture.

Old Ghost architecture only patched:
- page.click()
- page.fill()

But real-world enterprise frameworks mostly use:
- locator.click()
- locator.fill()
- locator.wait_for()

This test validates that Ghost now intercepts:
- Locator API
- runtime failures
- wait_for failures
- fill failures
- click failures

EXPECTED RESULT:
Ghost silently heals broken locators using the Render AI Brain.

Run:
    pytest demo/playwright-python/test_demo.py -v -s
"""

# ← NO ghost_healer import
# ← NO protect_page()
# ← ZERO framework-specific changes


def test_locator_api_healing(page):

    page.set_default_timeout(30000)

    page.goto("https://www.saucedemo.com/")

    # ─────────────────────────────────────────────
    # 🔴 BROKEN USERNAME LOCATOR
    # Correct = #user-name
    # ─────────────────────────────────────────────

    username_input = page.locator("#user-name-WRONG")

    username_input.wait_for(state="visible")

    username_input.fill("standard_user")

    # ─────────────────────────────────────────────
    # 🔴 BROKEN PASSWORD LOCATOR
    # Correct = #password
    # ─────────────────────────────────────────────

    password_input = page.locator("#password-WRONG")

    password_input.fill("secret_sauce")

    # ─────────────────────────────────────────────
    # 🔴 BROKEN LOGIN BUTTON
    # Correct = #login-button
    # ─────────────────────────────────────────────

    login_button = page.locator("#login-button-WRONG")

    login_button.click()

    # ─────────────────────────────────────────────
    # Validate login success
    # ─────────────────────────────────────────────

    assert (
        page.url
        == "https://www.saucedemo.com/inventory.html"
    )

    # ─────────────────────────────────────────────
    # 🔴 BROKEN ADD TO CART BUTTON
    # Correct = #add-to-cart-sauce-labs-backpack
    # ─────────────────────────────────────────────

    add_to_cart = page.locator(
        "#add-to-cart-sauce-labs-backpack-WRONG"
    )

    add_to_cart.click()

    print(
        "\n[SUCCESS] Ghost Healer Locator API validation passed."
    )