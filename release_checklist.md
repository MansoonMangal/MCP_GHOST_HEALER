# Ghost Healer Release Checklist

This project follows staged release gates:

- Beta: MCP-first Brain + Python/TS absolute-zero activation
- RC: Java/JS absolute-zero activation + security hardening
- GA: full matrix pass + docs complete + Render SLO verification

## 1) Beta Gate

Required:

1. MCP gateway and FastAPI runtime present.
2. Python and mcp-server test suites pass.
3. TS package builds successfully.
4. Migration/install docs are present and updated.

Run locally:

```bash
python scripts/release_gate.py --stage beta
```

## 2) RC Gate

Required:

1. Beta gate is green.
2. Java zero-change artifacts exist (`GhostHealerAgent`, service loader registration).
3. Security middleware enabled (auth + payload limit).
4. Java compile smoke check passes.

Run locally:

```bash
python scripts/release_gate.py --stage rc
```

## 3) GA Gate

Required:

1. RC gate is green.
2. Lint checks pass for core MCP surfaces.
3. CI matrix workflow is green.
4. Render SLO probe is green against deployed Brain.

Run locally:

```bash
python scripts/release_gate.py --stage ga
```

Run deployed SLO probe:

```bash
python scripts/verify_slo.py --base-url "https://your-brain.onrender.com" --max-p95-ms 700 --api-key "$GHOST_API_KEY"
```

## 4) CI Workflow

Manual gate workflow:

- `.github/workflows/release-gates.yml`

Usage:

1. Run workflow dispatch.
2. Select stage (`beta`, `rc`, or `ga`).
3. Provide `brain_url` for GA SLO check (optional but recommended).

## 5) Publish and Deploy

After GA gate is green:

1. Publish Python package.
2. Publish `ghost-healer-ts`.
3. Publish Java artifacts / agent jar.
4. Deploy Render Blueprint from `render.yaml`.
5. Validate production with:
   - `ghost-healer doctor`
   - `/health/ready`
   - `/api/mcp/v1/tools`

