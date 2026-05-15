/**
 * 👻 Ghost Healer — Playwright TypeScript Config
 *
 * The ONLY change needed in your existing playwright.config.ts is:
 *   globalSetup: require.resolve('ghost-healer-ts/setup')
 *
 * That's it. All your tests heal automatically.
 */
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // ← THIS IS THE ONLY LINE YOU ADD TO YOUR EXISTING CONFIG
  globalSetup: require.resolve('../../sdk/ts/src/setup'),

  use: {
    headless: true,
    screenshot: 'only-on-failure',
  },

  testDir: '.',
  timeout: 60000,
});
