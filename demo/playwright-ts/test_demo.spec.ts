/**
 * 👻 Ghost Healer Demo — Playwright TypeScript (ZERO code changes)
 *
 * This test uses STANDARD Playwright page.click() / page.fill().
 * NO GhostLocator import. NO wrapper. NOTHING changed in the test.
 *
 * Ghost healing is activated by ONE LINE in playwright.config.ts:
 *   globalSetup: require.resolve('../../sdk/ts/src/setup')
 *
 * The locators below are intentionally WRONG.
 * Ghost Healer heals them silently. Test passes.
 *
 * Run:
 *   npx playwright test demo/playwright-ts/test_demo.spec.ts
 */
import { test, expect } from '@playwright/test';

test('login with broken locators — standard page API, Ghost heals silently', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  // Standard page.fill() — 🔴 BROKEN selector, Ghost heals it automatically
  await page.fill('#user-name', 'standard_user');

  // Standard page.fill() — 🔴 BROKEN selector, Ghost heals  // 🔴 BROKEN: correct is #password
  await page.fill('#password', 'secret_sauce');

  // Use correct login button
  await page.click('#login-button');

  await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');

  // 🔴 BROKEN: correct is #add-to-cart-sauce-labs-backpack
  await page.click('#add-to-cart-sauce-labs-backpack');

  console.log('[SUCCESS] Login succeeded — standard page API, zero code changes!');
});
