'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const BUILTIN = (() => {
  const candidates = [
    path.join(__dirname, 'builtin-access.json'),
    path.join(__dirname, '..', 'builtin-access.json'),
  ];
  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) {
        return JSON.parse(fs.readFileSync(p, 'utf8'));
      }
    } catch {
      /* try next */
    }
  }
  return {
    brain_url: 'https://ghost-healer-brain.onrender.com',
    api_key: 'gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9',
  };
})();

const DEFAULT_BRAIN_URL = BUILTIN.brain_url;
const BUILTIN_API_KEY = BUILTIN.api_key;

function getGhostDir() {
  return path.join(os.homedir(), '.ghost');
}

function getCredentialsPath() {
  return path.join(getGhostDir(), 'credentials.json');
}

function loadGlobalCredentials() {
  try {
    const p = getCredentialsPath();
    if (!fs.existsSync(p)) return null;
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch {
    return null;
  }
}

function saveGlobalCredentials(creds) {
  const dir = getGhostDir();
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  const payload = {
    api_key: creds.api_key || BUILTIN_API_KEY,
    brain_url: creds.brain_url || DEFAULT_BRAIN_URL,
    tenant_id: creds.tenant_id || 'default',
    project_id: creds.project_id || 'default',
    source: creds.source || 'user',
    saved_at: new Date().toISOString(),
  };
  fs.writeFileSync(getCredentialsPath(), JSON.stringify(payload, null, 2), { mode: 0o600 });
  return payload;
}

/** Auto-provision SDK access on first install — no manual login required. */
function ensureBuiltinCredentials() {
  if (loadGlobalCredentials()) return loadGlobalCredentials();
  return saveGlobalCredentials({
    api_key: BUILTIN_API_KEY,
    brain_url: DEFAULT_BRAIN_URL,
    tenant_id: 'sdk',
    project_id: 'default',
    source: 'builtin',
  });
}

function getBuiltinAccess() {
  return { brain_url: DEFAULT_BRAIN_URL, api_key: BUILTIN_API_KEY };
}

/** Apply credentials: user file → builtin SDK access (install-only). */
function applyGlobalCredentials() {
  const creds = loadGlobalCredentials();
  if (creds) {
    if (creds.api_key && !process.env.GHOST_API_KEY) {
      process.env.GHOST_API_KEY = creds.api_key;
    }
    if (creds.brain_url && !process.env.GHOST_BRAIN_URL) {
      process.env.GHOST_BRAIN_URL = creds.brain_url;
    }
    if (creds.tenant_id && !process.env.GHOST_TENANT_ID) {
      process.env.GHOST_TENANT_ID = creds.tenant_id;
    }
    if (creds.project_id && !process.env.GHOST_PROJECT_ID) {
      process.env.GHOST_PROJECT_ID = creds.project_id;
    }
  }

  if (!process.env.GHOST_API_KEY) {
    process.env.GHOST_API_KEY = BUILTIN_API_KEY;
  }
  if (!process.env.GHOST_BRAIN_URL) {
    process.env.GHOST_BRAIN_URL = DEFAULT_BRAIN_URL;
  }
}

function hasApiKey() {
  applyGlobalCredentials();
  return Boolean((process.env.GHOST_API_KEY || '').trim());
}

module.exports = {
  DEFAULT_BRAIN_URL,
  BUILTIN_API_KEY,
  getGhostDir,
  getCredentialsPath,
  loadGlobalCredentials,
  saveGlobalCredentials,
  ensureBuiltinCredentials,
  getBuiltinAccess,
  applyGlobalCredentials,
  hasApiKey,
};
