'use strict';

const fs = require('fs');
const path = require('path');
const { applyGlobalCredentials } = require('./credentials');

let _loaded = false;

function findProjectRoot(startDir) {
  let dir = startDir || process.cwd();
  for (let i = 0; i < 20; i++) {
    if (
      fs.existsSync(path.join(dir, 'package.json')) ||
      fs.existsSync(path.join(dir, 'ghost.yaml')) ||
      fs.existsSync(path.join(dir, '.git'))
    ) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

function parseEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  const content = fs.readFileSync(filePath, 'utf8');
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined || process.env[key] === '') {
      process.env[key] = value;
    }
  }
}

/** Load credentials: machine login → .env → env vars */
function loadProjectEnv(startDir) {
  if (_loaded) return findProjectRoot(startDir);
  _loaded = true;

  applyGlobalCredentials();

  const root = findProjectRoot(startDir);
  const envFile = process.env.ENV_FILE || '.env';
  parseEnvFile(path.join(root, envFile));
  parseEnvFile(path.join(root, '.env'));

  applyGlobalCredentials();
  return root;
}

function getApiKeyFromEnv() {
  loadProjectEnv();
  return (process.env.GHOST_API_KEY || '').trim();
}

module.exports = { loadProjectEnv, findProjectRoot, getApiKeyFromEnv };
