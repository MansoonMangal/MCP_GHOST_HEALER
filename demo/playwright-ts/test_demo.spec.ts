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
  await page.fill('#user-name-WRONG', 'standard_user');

  // Standard page.fill() — 🔴 BROKEN selector, Ghost heals it automatically
  await page.fill('#password-WRONG', 'secret_sauce');

  // Standard page.click() — 🔴 BROKEN selector, Ghost heals it automatically
  await page.click('#login-btn-WRONG');

  await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  console.log('✅ Login succeeded — standard page API, zero code changes!');
});
