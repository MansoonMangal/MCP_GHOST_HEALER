// 👻 Ghost Healer — Playwright JS Config
const { defineConfig } = require('@playwright/test');
require('../../sdk/ts/src/pw-hook.js');

module.exports = defineConfig({
  use: { headless: false },
  testDir: '.',
  timeout: 60000,
});
