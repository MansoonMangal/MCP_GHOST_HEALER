'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const DEFAULT_BRAIN_URL = 'https://ghost-healer-brain.onrender.com';

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
    api_key: creds.api_key || '',
    brain_url: creds.brain_url || DEFAULT_BRAIN_URL,
    tenant_id: creds.tenant_id || 'default',
    project_id: creds.project_id || 'default',
    saved_at: new Date().toISOString(),
  };
  fs.writeFileSync(getCredentialsPath(), JSON.stringify(payload, null, 2), { mode: 0o600 });
  return payload;
}

/** Apply ~/.ghost/credentials.json and optional enterprise URL to process.env */
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

  // Enterprise: IT hosts a JSON credentials file (internal HTTPS)
  const credUrl = process.env.GHOST_CREDENTIALS_URL;
  if (credUrl && !process.env.GHOST_API_KEY) {
    try {
      const https = require('https');
      const http = require('http');
      const client = credUrl.startsWith('https') ? https : http;
      // Sync fetch not available — skip in sync path; async handled in fetchCredentialsUrl
    } catch {
      /* optional */
    }
  }
}

function hasApiKey() {
  applyGlobalCredentials();
  return Boolean((process.env.GHOST_API_KEY || '').trim());
}

module.exports = {
  DEFAULT_BRAIN_URL,
  getGhostDir,
  getCredentialsPath,
  loadGlobalCredentials,
  saveGlobalCredentials,
  applyGlobalCredentials,
  hasApiKey,
};
