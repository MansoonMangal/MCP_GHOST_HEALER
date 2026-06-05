/**
 * Absolute zero-change activation for Node.js test runners.
 *
 * Activated via NODE_OPTIONS=--require ghost-healer-ts-sdk/auto-activate
 * (merged into .env on npm install postinstall).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { loadProjectEnv } = require('./projectEnv');
const { hasApiKey } = require('./credentials');

const pkgName = require('../package.json').name;

loadProjectEnv();

function findGhostYaml() {
  let dir = process.cwd();
  for (let i = 0; i < 20; i++) {
    const p = path.join(dir, 'ghost.yaml');
    if (fs.existsSync(p)) return p;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

function patchPlaywrightDefineConfig() {
  try {
    const pw = require('@playwright/test');
    if (pw.__ghostPatched || typeof pw.defineConfig !== 'function') return;

    const setupPath = require.resolve(`${pkgName}/dist/setup`);
    const teardownPath = require.resolve(`${pkgName}/dist/teardown`);
    const original = pw.defineConfig;

    pw.defineConfig = function ghostDefineConfig(config, ...rest) {
      const cfg = config || {};
      if (!cfg.globalSetup) cfg.globalSetup = setupPath;
      if (!cfg.globalTeardown) cfg.globalTeardown = teardownPath;
      return original.call(this, cfg, ...rest);
    };
    pw.__ghostPatched = true;
    console.log('[GHOST] auto-activate: globalSetup/globalTeardown injected (no playwright.config edits needed)');
  } catch (_) {
    /* @playwright/test optional */
  }
}

// Playwright: patch prototypes + inject global hooks
try {
  require('./pw-hook.js');
  patchPlaywrightDefineConfig();
  console.log('[GHOST] auto-activate: Playwright hooks loaded');
} catch (e) {
  console.warn('[GHOST] auto-activate: Playwright hook skipped:', e.message);
}

// Selenium
try {
  const selPath = path.join(__dirname, '..', 'dist', 'selenium-setup.js');
  require(selPath);
  console.log('[GHOST] auto-activate: Selenium hooks loaded');
} catch (_) {
  /* optional */
}

const yamlPath = findGhostYaml();
if (yamlPath) {
  console.log('[GHOST] auto-activate: config', yamlPath);
} else if (!hasApiKey()) {
  console.log('[GHOST] auto-activate: run once — npx ghost-healer login');
} else {
  console.log('[GHOST] auto-activate: ready');
}
