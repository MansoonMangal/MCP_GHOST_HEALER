import { test, expect } from '@playwright/test';
import { GhostLocator } from '../../sdk/ts/src/GhostLocator';

/**
 * 👻 Ghost Healer Demo — Playwright TypeScript
 *
 * Uses intentionally BROKEN locators.
 * GhostLocator intercepts failures and heals via the AI Brain.
 *
 * Run:
 *   npx playwright test demo/playwright-ts/test_demo.spec.ts
 */

test('login with broken locators — Ghost heals them', async ({ page }) => {
  const ghost = new GhostLocator(page, {
    brainUrl: process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com',
    confidenceThreshold: 0.5,
  });

  await page.goto('https://www.saucedemo.com/');

  // 🔴 BROKEN: correct is #user-name
  await ghost.fill('#username-field-WRONG', 'standard_user');

  // 🔴 BROKEN: correct is #password
  await ghost.fill('#pass-field-WRONG', 'secret_sauce');

  // 🔴 BROKEN: correct is #login-button
  await ghost.click('#submit-btn-WRONG');

  await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  console.log('✅ Login succeeded via Ghost Healer TS SDK!');
});
