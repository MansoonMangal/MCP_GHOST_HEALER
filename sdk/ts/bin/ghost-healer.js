#!/usr/bin/env node
'use strict';

/**
 * Ghost Healer CLI — enterprise one-time login (stores ~/.ghost/credentials.json)
 *
 *   npx ghost-healer login
 *   npx ghost-healer login --key=YOUR_KEY
 *   npx ghost-healer doctor
 *   npx ghost-healer status
 */
const fs = require('fs');
const readline = require('readline');
const {
  DEFAULT_BRAIN_URL,
  getCredentialsPath,
  loadGlobalCredentials,
  saveGlobalCredentials,
  applyGlobalCredentials,
  ensureBuiltinCredentials,
  hasApiKey,
} = require('../src/credentials');
const { loadProjectEnv } = require('../src/projectEnv');

const cmd = process.argv[2] || 'help';

function parseFlag(name) {
  const prefix = `--${name}=`;
  const arg = process.argv.find((a) => a.startsWith(prefix));
  return arg ? arg.slice(prefix.length) : process.env[`GHOST_${name.toUpperCase()}`] || '';
}

async function promptHidden(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function login() {
  let apiKey = parseFlag('key') || parseFlag('api-key');
  const brainUrl = parseFlag('brain-url') || parseFlag('url') || DEFAULT_BRAIN_URL;
  const tenantId = parseFlag('tenant') || 'default';
  const projectId = parseFlag('project') || 'default';

  if (!apiKey) {
    console.log('\n👻 Ghost Healer — one-time login');
    console.log('Get your key from your team admin or Render dashboard.\n');
    apiKey = await promptHidden('Paste GHOST_API_KEY (input visible): ');
  }

  if (!apiKey) {
    console.error('❌ No API key provided.');
    process.exit(1);
  }

  saveGlobalCredentials({
    api_key: apiKey,
    brain_url: brainUrl,
    tenant_id: tenantId,
    project_id: projectId,
  });

  applyGlobalCredentials();
  console.log(`✅ Saved to ${getCredentialsPath()}`);
  console.log('   All Playwright/Selenium projects on this machine can heal — no .env edits needed.');
  console.log('   Run: npm install ghost-healer-ts-sdk && npx playwright test\n');
}

async function doctor() {
  ensureBuiltinCredentials();
  loadProjectEnv();
  applyGlobalCredentials();
  const creds = loadGlobalCredentials();
  const brainUrl = process.env.GHOST_BRAIN_URL || creds?.brain_url || DEFAULT_BRAIN_URL;
  const key = (process.env.GHOST_API_KEY || '').trim();
  const source = creds?.source === 'user' ? 'custom' : 'SDK built-in (install-only)';

  console.log('\n👻 Ghost Healer Doctor\n');
  console.log(`  Brain URL  : ${brainUrl}`);
  console.log(`  Access     : ${source}`);
  console.log(`  API key    : ${key ? 'configured ✓' : 'MISSING'}`);

  if (!key) {
    process.exit(1);
  }

  try {
    const resp = await fetch(`${brainUrl.replace(/\/$/, '')}/health`, {
      headers: { 'X-API-Key': key },
    });
    const data = await resp.json();
    if (resp.ok) {
      console.log(`  Brain      : ${data.status} (storage: ${data.storage_backend || 'n/a'}) ✓\n`);
    } else {
      console.log(`  Brain      : HTTP ${resp.status} — check API key\n`);
      process.exit(1);
    }
  } catch (e) {
    console.log(`  Brain      : unreachable (${e.message})\n`);
    process.exit(1);
  }
}

function status() {
  const creds = loadGlobalCredentials();
  if (!creds) {
    console.log('Not logged in. Run: npx ghost-healer login');
    process.exit(1);
  }
  console.log(JSON.stringify({ ...creds, api_key: creds.api_key ? '***configured***' : '' }, null, 2));
}

function help() {
  console.log(`
Ghost Healer CLI

  npx ghost-healer doctor             Verify Brain connection (no login needed)
  npx ghost-healer login              Optional: use a private Brain / custom API key
  npx ghost-healer login --key=KEY    Non-interactive custom key
  npx ghost-healer status             Show saved profile (key hidden)

Install ghost-healer-ts-sdk — healing works automatically, no API key setup.
`);
}

(async () => {
  switch (cmd) {
    case 'login':
      await login();
      break;
    case 'doctor':
      await doctor();
      break;
    case 'status':
      status();
      break;
    default:
      help();
  }
})();
