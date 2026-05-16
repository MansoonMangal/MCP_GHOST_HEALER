/**
 * 👻 Ghost Healer — Playwright TypeScript Config
 *
 * The ONLY change needed in your existing playwright.config.ts is:
 *   require('ghost-healer-ts/pw-hook.js')
 *
 * That's it. All your tests heal automatically.
 */
import { defineConfig } from '@playwright/test';
require('../../sdk/ts/src/pw-hook.js');

export default defineConfig({
  use: {
    headless: false,
    screenshot: 'only-on-failure',
  },

  testDir: '.',
  timeout: 60000,
});
