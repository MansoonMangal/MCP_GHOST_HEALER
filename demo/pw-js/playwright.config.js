// 👻 Ghost Healer — Playwright JS Config
// The ONLY change needed in your existing config:
//   globalSetup: require.resolve('ghost-healer-ts/setup')
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  // ← ADD THIS ONE LINE to your existing playwright.config.js
  globalSetup: require.resolve('../../sdk/ts/src/setup'),
  use: { headless: true },
  testDir: '.',
  timeout: 60000,
});
