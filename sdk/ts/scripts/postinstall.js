'use strict';

const fs = require('fs');
const path = require('path');

const pkgRoot = path.join(__dirname, '..');
const pkgName = require(path.join(pkgRoot, 'package.json')).name;
const autoRequire = `--require ${pkgName}/auto-activate`;

function findProjectRoot() {
  let dir = process.cwd();
  for (let i = 0; i < 20; i++) {
    if (fs.existsSync(path.join(dir, 'package.json'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

function parseEnvKeys(content) {
  const keys = new Set();
  for (const line of content.split(/\r?\n/)) {
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=/);
    if (m) keys.add(m[1]);
  }
  return keys;
}

function mergeNodeOptionsValue(existing) {
  const val = (existing || '').trim();
  if (val.includes(`${pkgName}/auto-activate`)) return val;
  return val ? `${val} ${autoRequire}` : autoRequire;
}

function run() {
  const root = findProjectRoot();
  const envPath = path.join(root, '.env');
  let content = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';
  const keys = parseEnvKeys(content);
  const additions = [];
  let changed = false;

  if (!keys.has('NODE_OPTIONS')) {
    additions.push(`NODE_OPTIONS=${autoRequire}`);
  } else {
    const lines = content.split(/\r?\n/);
    const next = lines.map((line) => {
      if (line.startsWith('NODE_OPTIONS=')) {
        const val = line.slice('NODE_OPTIONS='.length);
        const merged = mergeNodeOptionsValue(val);
        if (merged !== val.trim()) changed = true;
        return `NODE_OPTIONS=${merged}`;
      }
      return line;
    });
    if (changed) content = next.join('\n');
  }

  if (additions.length) {
    const prefix = content && !content.endsWith('\n') ? '\n' : '';
    content = content + prefix + additions.join('\n') + '\n';
    changed = true;
  }

  if (changed) {
    fs.writeFileSync(envPath, content, 'utf8');
  }

  console.log('[GHOST] Zero-change healing enabled for this project.');
  console.log('[GHOST] One-time on this machine:  npx ghost-healer login');
  console.log('[GHOST] Or IT sets GHOST_API_KEY system-wide / CI secret — no .env needed.');
}

try {
  run();
} catch (err) {
  console.warn('[GHOST] postinstall skipped:', err.message);
}
