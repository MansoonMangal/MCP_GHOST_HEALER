/**
 * 👻 Ghost Healer — Playwright TypeScript Demo Config
 *
 * Two lines is ALL you need to activate AI self-healing:
 *
 *   Line 1:  require('ghost-healer-ts/pw-hook.js')       ← intercepts all locator calls
 *   Line 2:  globalSetup + globalTeardown paths           ← lifecycle hooks
 *
 * That's it. All your tests heal automatically after they run.
 */
import { defineConfig } from '@playwright/test';

// Activate the prototype interceptors for every worker
require('../../sdk/ts/src/pw-hook.js');

export default defineConfig({
  use: {
    headless: false,
    screenshot: 'only-on-failure',
    actionTimeout: 5000,
  },

  // Playwright expects file-path strings for globalSetup/Teardown
  globalSetup:    require.resolve('../../sdk/ts/src/setup'),
  globalTeardown: require.resolve('../../sdk/ts/src/teardown'),

  testDir: 'tests',
  timeout: 60000,

  // Allow tests to continue after failure so Ghost can collect ALL failures
  reporter: [['list'], ['html', { outputFolder: '../../reports/playwright-html', open: 'never' }]],
});
