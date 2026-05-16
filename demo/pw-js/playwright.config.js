// 👻 Ghost Healer — Playwright JS Config
// The ONLY change needed in your existing config:
//   globalSetup: require.resolve('ghost-healer-ts/setup')
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: { headless: false },
  testDir: '.',
  timeout: 60000,
});
