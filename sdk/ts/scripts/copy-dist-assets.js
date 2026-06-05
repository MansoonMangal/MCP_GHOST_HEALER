'use strict';

/**
 * Copy JS runtime assets into dist/ so compiled modules (e.g. brainAuth.js)
 * can require('./credentials') from the same directory.
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const dist = path.join(root, 'dist');

const copies = [
  ['src/credentials.js', 'dist/credentials.js'],
  ['src/projectEnv.js', 'dist/projectEnv.js'],
  ['builtin-access.json', 'dist/builtin-access.json'],
];

for (const [from, to] of copies) {
  const src = path.join(root, from);
  const dest = path.join(root, to);
  if (!fs.existsSync(src)) {
    console.warn(`[GHOST build] skip missing: ${from}`);
    continue;
  }
  fs.mkdirSync(dist, { recursive: true });
  fs.copyFileSync(src, dest);
  console.log(`[GHOST build] copied ${from} → ${to}`);
}
