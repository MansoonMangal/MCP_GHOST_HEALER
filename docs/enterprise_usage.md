# Ghost Healer Enterprise Usage Guidelines

This guide describes safe production usage, governance, and CI/CD patterns.

## Healing Modes

### `runtime`

- Immediately retries with healed locator.
- Optional source patch when `auto_patch: true`.
- Best for local development or lower-risk regression suites.

### `suggestion`

- No automatic retry.
- Suggestion is logged and added to pending review queue.
- Best for CI where deterministic behavior is required.

### `approval`

- Same execution behavior as `suggestion`.
- Intended for explicit accept/reject workflows via `ghost-healer review` and pending-fix APIs.

### `strict`

- Allows only very high-confidence heals.
- Fails quickly when certainty is low.
- Recommended for critical release gates.

## Tenant and Project Isolation

For multi-team usage, set at login time or via env:

- `GHOST_TENANT_ID` → sent as `X-Ghost-Tenant`
- `GHOST_PROJECT_ID` → sent as `X-Ghost-Project`

Example:

```bash
npx ghost-healer login --tenant=acme-qa --project=checkout-suite
```

These values scope feedback and analytics, and prepare the platform for per-tenant policy controls.

## Security Baseline

Use these production settings on Brain:

- `GHOST_API_KEY` (required)
- `CORS_ORIGINS` (restrict to allowed origins)
- `MAX_REQUEST_BYTES` (guard large DOM payloads)

Client-side credential delivery (pick one):

| Tier | Setup | Notes |
|------|--------|-------|
| **Developer laptop** | `npx ghost-healer login` or `ghost-healer login` once | Stores `~/.ghost/credentials.json` (mode 600) |
| **Enterprise fleet** | IT sets machine-wide `GHOST_API_KEY` via GPO/Intune/etc. | No per-project `.env` |
| **CI/CD** | Pipeline secret `GHOST_API_KEY` | Same key as Brain Render env |
| **Bulk onboarding** | `ghost-healer login --key=$KEY` in IT script | Non-interactive |

- Never commit secrets into `ghost.yaml` or git-tracked `.env`.
- Rotate keys in Render → re-run `login` or update CI secret.

## Governance and Feedback

Use built-in APIs:

- `POST /api/heal-feedback` (accepted/rejected)
- `GET /api/heal-feedback-summary`
- `GET /api/pending-fixes`

Track:

- acceptance rate by project
- high-risk unstable locators
- manual review backlog

## CI/CD Recommendation

### Pull Request Validation

- mode: `strict` or `suggestion`
- run stage gate:
  - `python scripts/release_gate.py --stage beta`

### Release Candidate Validation

- enable Java/JS checks
- run:
  - `python scripts/release_gate.py --stage rc`

### Production Promotion

- run:
  - `python scripts/release_gate.py --stage ga`
- deployed SLO probe:
  - `python scripts/verify_slo.py --base-url "<render-url>" --api-key "$GHOST_API_KEY"`
