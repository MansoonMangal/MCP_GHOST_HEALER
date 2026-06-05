#!/usr/bin/env node
'use strict';

/**
 * Run Playwright with Ghost Healer auto-activation (no config edits required).
 * Usage: npx ghost-playwright test
 */
const { spawnSync } = require('child_process');
const path = require('path');

const pkgName = require(path.join(__dirname, '..', 'package.json')).name;
const autoRequire = `--require ${pkgName}/auto-activate`;
const existing = process.env.NODE_OPTIONS || '';
if (!existing.includes(`${pkgName}/auto-activate`)) {
  process.env.NODE_OPTIONS = existing ? `${existing} ${autoRequire}` : autoRequire;
}

const args = ['playwright', ...process.argv.slice(2)];
const result = spawnSync('npx', args, { stdio: 'inherit', shell: true, env: process.env });
process.exit(result.status ?? 1);
