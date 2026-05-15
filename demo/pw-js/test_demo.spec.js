/**
 * 👻 Ghost Healer Demo — Playwright JavaScript (ZERO code changes)
 *
 * Standard Playwright JS test. No Ghost Healer imports.
 * Healing is activated via playwright.config.js globalSetup.
 *
 * Run: npx playwright test demo/pw-js/test_demo.spec.js
 */
const { test, expect } = require('@playwright/test');

test('login with broken locators — JS, Ghost heals silently', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  // Standard page.fill() — broken, Ghost heals automatically
  await page.fill('#user-name-WRONG', 'standard_user');
  await page.fill('#password-WRONG', 'secret_sauce');

  // Standard page.click() — broken, Ghost heals automatically
  await page.click('#login-btn-WRONG');

  await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  console.log('✅ PW + JS: Passed with zero Ghost Healer code!');
});
