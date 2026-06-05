/**
 * Absolute zero-change activation for Node.js test runners.
 *
 * Activated automatically when ghost-healer-ts is installed (postinstall sets
 * NODE_OPTIONS) or manually:
 *   set NODE_OPTIONS=--require ghost-healer-ts/auto-activate
 */
'use strict';

const fs = require('fs');
const path = require('path');

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

// Playwright: load pw-hook (patches Page/Locator at require time)
try {
  require('./pw-hook.js');
  console.log('[GHOST] auto-activate: Playwright hooks loaded');
} catch (e) {
  console.warn('[GHOST] auto-activate: Playwright hook skipped:', e.message);
}

// Selenium: load compiled selenium-setup (dynamic path — avoid tsc pulling dist/ as input)
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
} else {
  console.log('[GHOST] auto-activate: using defaults (no ghost.yaml)');
}
