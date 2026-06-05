/**
 * Shared Brain auth headers for TS/JS SDK HTTP calls.
 */
export function getApiKey(config?: { mcp_server?: { api_key?: string } }): string {
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
  return headers;
}
