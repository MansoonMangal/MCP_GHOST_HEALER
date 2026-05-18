/**
 * 👻 Ghost Healer Demo — Locator API Validation
 *
 * PURPOSE:
 * This demo intentionally uses Locator API instead of page.click/page.fill
 * to validate the NEW enterprise Ghost architecture.
 *
 * WHY?
 * Old Ghost architecture only patched page methods.
 * Real enterprise frameworks mostly use locator methods.
 *
 * This test validates:
 * - locator.fill()
 * - locator.click()
 * - locator.waitFor()
 *
 * EXPECTED RESULT:
 * Ghost heals broken locators silently using Render AI Brain.
 *
 * Run:
 * npx playwright test demo/playwright-ts/test_demo.spec.ts --headed
 */

import { test, expect } from '@playwright/test';

test(
  'locator API healing — Ghost heals silently',
  async ({ page }) => {
    await page.goto('https://www.saucedemo.com/');

    // ─────────────────────────────────────────────
    // 🔴 INTENTIONALLY BROKEN USERNAME LOCATOR
    // Correct = #user-name
    // ─────────────────────────────────────────────

    const usernameInput =
      page.locator('#user-name');

    await usernameInput.waitFor({
      state: 'visible',
    });

    await usernameInput.fill('standard_user');

    // ─────────────────────────────────────────────
    // 🔴 INTENTIONALLY BROKEN PASSWORD LOCATOR
    // Correct = #password
    // ─────────────────────────────────────────────

    const passwordInput =
      page.locator('#password');

    await passwordInput.fill('secret_sauce');

    // ─────────────────────────────────────────────
    // 🔴 INTENTIONALLY BROKEN LOGIN BUTTON
    // Correct = #login-button
    // ─────────────────────────────────────────────

    const loginButton =
      page.locator('#login-button');

    await loginButton.click();

    // ─────────────────────────────────────────────
    // Validate successful login
    // ─────────────────────────────────────────────

    await expect(page).toHaveURL(
      'https://www.saucedemo.com/inventory.html'
    );

    // ─────────────────────────────────────────────
    // 🔴 INTENTIONALLY BROKEN PRODUCT BUTTON
    // Correct = #add-to-cart-sauce-labs-backpack
    // ─────────────────────────────────────────────

    const addToCartButton =
      page.locator(
        '#item_4_img_link'
      );

    await addToCartButton.click();

    console.log(
      '[SUCCESS] Ghost Healer Locator API test passed.'
    );
  }
);
