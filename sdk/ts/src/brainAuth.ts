/**
 * Shared Brain auth headers for TS/JS SDK HTTP calls.
 */
import * as fs from 'fs';
import * as path from 'path';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { applyGlobalCredentials, loadGlobalCredentials } = require('./credentials');

let _envLoaded = false;

function findProjectRoot(startDir?: string): string {
  let dir = startDir || process.cwd();
  for (let i = 0; i < 20; i++) {
    if (
      fs.existsSync(path.join(dir, 'ghost.yaml')) ||
      fs.existsSync(path.join(dir, '.git')) ||
      fs.existsSync(path.join(dir, 'package.json'))
    ) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

function parseEnvFile(filePath: string): void {
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

/** Load credentials + project .env (idempotent). */
export function loadGhostEnv(startDir?: string): void {
  if (_envLoaded) return;
  _envLoaded = true;

  applyGlobalCredentials();

  const root = findProjectRoot(startDir);
  const envFile = process.env.ENV_FILE || '.env';
  parseEnvFile(path.join(root, envFile));
  parseEnvFile(path.join(root, '.env'));

  const yamlPath = path.join(root, 'ghost.yaml');
  if (fs.existsSync(yamlPath) && !process.env.GHOST_API_KEY) {
    try {
      const yaml = require('js-yaml') as typeof import('js-yaml');
      const data = yaml.load(fs.readFileSync(yamlPath, 'utf8')) as {
        mcp_server?: { api_key?: string };
      };
      const key = data?.mcp_server?.api_key?.trim();
      if (key) process.env.GHOST_API_KEY = key;
    } catch {
      /* optional */
    }
  }

  applyGlobalCredentials();
}

export function getApiKey(config?: { mcp_server?: { api_key?: string } }): string {
  loadGhostEnv();
  const fromEnv = (process.env.GHOST_API_KEY || '').trim();
  const fromYaml = config?.mcp_server?.api_key || '';
  return fromEnv || String(fromYaml).trim();
}

export function brainHeaders(
  config?: { mcp_server?: { api_key?: string } }
): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Ghost-Protocol': 'mcp-v1',
  };
  const apiKey = getApiKey(config);
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  const creds = loadGlobalCredentials();
  const tenant = process.env.GHOST_TENANT_ID || creds?.tenant_id || 'default';
  const project = process.env.GHOST_PROJECT_ID || creds?.project_id || 'default';
  headers['X-Ghost-Tenant'] = tenant;
  headers['X-Ghost-Project'] = project;
  return headers;
}

export function warnIfMissingApiKey(): void {
  loadGhostEnv();
  if (!getApiKey()) {
    console.warn(
      '[GHOST] ⚠️  No API key found. Run once: npx ghost-healer login  (or IT sets GHOST_API_KEY machine-wide).'
    );
  }
}
