# Migration Guide: MCP v1 (Ghost Healer 1.2 / Brain 4.0)

## What Changed

- **Brain** is MCP-first: tools at `/mcp` (Streamable HTTP) and REST shim at `/api/mcp/v1/tools/{name}`.
- **Legacy Flask** (`mcp-server/main.py`) is deprecated; use `app.main:app` only.
- **Confidence** in API responses is always **0.0–1.0**.
- **Python SDK** calls MCP shim first, then `/api/heal-locator`.
- **Zero-change activation**: install SDK only; no test script edits.

## SDK Install (per language)

### Python
```bash
pip install ghost-healer
pytest your_tests/   # plugin auto-activates
```

### TypeScript / JavaScript
```bash
npm install ghost-healer-ts
# postinstall sets NODE_OPTIONS for auto-activate
npx playwright test
```

### Java
```bash
# JUnit 5 service-loader auto-registers GhostHealerExtension when JAR is on classpath
# Or use javaagent for all WebDriver fields without @GhostDriver:
export JAVA_TOOL_OPTIONS="-javaagent:ghost-healer-agent.jar"
mvn test
```

## Configuration

`ghost.yaml`:
```yaml
mcp_server:
  url: "https://ghost-healer-brain.onrender.com"
  protocol: "mcp-first"
  confidence_threshold: 0.5
  api_key: ""   # or set GHOST_API_KEY env
```

Environment overrides:
- `GHOST_BRAIN_URL` / `MCP_SERVER_URL` — brain URL
- `GHOST_API_KEY` — API key for production Render brain

## Render Deployment

1. Push repo; connect Render Blueprint (`render.yaml`).
2. Copy generated `GHOST_API_KEY` from Render dashboard.
3. Set `GHOST_API_KEY` in client CI and local `ghost.yaml` or env.

## Rollout Phases

| Phase | Scope |
|-------|--------|
| Beta | Python + TS MCP-first + Render staging |
| RC | Java agent + security hardening |
| GA | Full 8-combo matrix green in CI |

## Breaking Changes

- `confidence_threshold` must be **0–1** (invalid values rejected).
- Flask-only endpoints removed; use FastAPI routes listed in `/docs`.

## Verify

```bash
ghost-healer doctor
curl https://your-brain.onrender.com/health
curl https://your-brain.onrender.com/api/mcp/v1/tools
```
