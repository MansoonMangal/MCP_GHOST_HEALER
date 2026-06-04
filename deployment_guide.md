# Production Deployment Guide: Ghost Healer

Deploy the MCP-first Brain and configure SDK clients for production usage.

## 1) Deploy Brain on Render

Use the included `render.yaml`.

1. Push repository to GitHub.
2. In Render, choose **New -> Blueprint** and connect the repo.
3. Render provisions:
   - Web service (`ghost-healer-brain`)
   - MongoDB (from blueprint)
4. After first deploy, copy:
   - service URL (for SDK clients)
   - generated `GHOST_API_KEY`

## 2) Required Production Environment Variables

Set on Render service:

- `GHOST_API_KEY` (required)
- `MONGO_URI` (from Render DB)
- `LOG_LEVEL=INFO`
- `MCP_DEBUG=false`
- `CORS_ORIGINS` (restrict in enterprise)
- `MAX_REQUEST_BYTES` (e.g. `5242880`)

## 3) Client Configuration

In CI/CD (GitHub Actions/Jenkins/etc):

```bash
export GHOST_BRAIN_URL="https://your-ghost-brain.onrender.com"
export GHOST_API_KEY="<render-secret>"
```

Or in `ghost.yaml`:

```yaml
mcp_server:
  url: "https://your-ghost-brain.onrender.com"
  protocol: "mcp-first"
  api_key: ""
```

Prefer env vars for secrets.

## 4) Health and Smoke Validation

Check endpoints:

- `/health`
- `/health/ready`
- `/api/mcp/v1/tools`
- `/docs`

Run local gate and SLO checks:

```bash
python scripts/release_gate.py --stage ga
python scripts/verify_slo.py --base-url "https://your-ghost-brain.onrender.com" --api-key "$GHOST_API_KEY"
```

## 5) Package Distribution

### Python (`ghost-healer`)

```bash
pip install build twine
python -m build
twine upload dist/*
```

### TypeScript / JavaScript (`ghost-healer-ts`)

```bash
cd sdk/ts
npm install
npm run build
npm publish
```

### Java

Publish framework/agent artifacts to Maven Central or internal Nexus.

## 6) Recommended Release Order

Follow staged release gates:

1. Beta (`release_gate.py --stage beta`)
2. RC (`release_gate.py --stage rc`)
3. GA (`release_gate.py --stage ga`)

Reference: `release_checklist.md`.
