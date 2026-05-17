/**
 * 👻 Ghost Healer Demo — Playwright JavaScript Locator API Validation
 *
 * PURPOSE:
 * Validate the NEW enterprise Ghost architecture.
 *
 * Old Ghost architecture only intercepted:
 * - page.click()
 * - page.fill()
 *
 * Real-world Playwright JS frameworks mostly use:
 * - locator.click()
 * - locator.fill()
 * - locator.waitFor()
 *
 * This demo validates:
 * - Locator API interception
 * - runtime healing
 * - AI recovery flow
 * - Render Brain integration
 *
 * EXPECTED RESULT:
 * Ghost silently heals broken locators using the cloud AI Brain.
 *
 * Run:
 * npx playwright test demo/pw-js/test_demo.spec.js --headed
 */

const { test, expect } =
  require('@playwright/test');

test(
  'locator API healing — JS Ghost heals silently',
  async ({ page }) => {

    await page.goto(
      'https://www.saucedemo.com/'
    );

    // ─────────────────────────────────────────
    // 🔴 BROKEN USERNAME LOCATOR
    // Correct = #user-name
    // ─────────────────────────────────────────

    const usernameInput =
      page.locator('#user-name-WRONG');

    await usernameInput.waitFor({
      state: 'visible',
    });

    await usernameInput.fill(
      'standard_user'
    );

    // ─────────────────────────────────────────
    // 🔴 BROKEN PASSWORD LOCATOR
    // Correct = #password
    // ─────────────────────────────────────────

    const passwordInput =
      page.locator('#password-WRONG');

    await passwordInput.fill(
      'secret_sauce'
    );

    // ─────────────────────────────────────────
    // 🔴 BROKEN LOGIN BUTTON
    // Correct = #login-button
    // ─────────────────────────────────────────

    const loginButton =
      page.locator('#login-button-WRONG');

    await loginButton.click();

    // ─────────────────────────────────────────
    // Validate successful login
    // ─────────────────────────────────────────

    await expect(page).toHaveURL(
      'https://www.saucedemo.com/inventory.html'
    );

    // ─────────────────────────────────────────
    // 🔴 BROKEN ADD TO CART BUTTON
    // Correct = #add-to-cart-sauce-labs-backpack
    // ─────────────────────────────────────────

    const addToCartButton =
      page.locator(
        '#add-to-cart-sauce-labs-backpack-WRONG'
      );

    await addToCartButton.click();

    console.log(
      '[SUCCESS] Ghost Healer JS Locator API validation passed.'
    );
  }
);