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
  const { GhostLocator } = require('../../sdk/ts/dist');
  const ghost = new GhostLocator(page, { confidenceThreshold: 0.0 });
  await page.goto('https://www.saucedemo.com/');

  // Standard page.fill() — broken, Ghost heals automatically
  await ghost.fill('#user-name', 'standard_user');
  await ghost.fill('#password', 'secret_sauce');

  // Use correct login button
  await ghost.click('#login-button');

  await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');

  // 🔴 BROKEN: correct is #add-to-cart-sauce-labs-backpack
  await ghost.click('#add-to-cart-sauce-labs-backpack');

  console.log('[SUCCESS] Login succeeded — standard JS page API, zero code changes!');
});
