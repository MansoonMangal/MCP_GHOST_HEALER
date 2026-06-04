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

For multi-team usage, send:

- `X-Ghost-Tenant`
- `X-Ghost-Project`

These values scope feedback and analytics, and prepare the platform for per-tenant policy controls.

## Security Baseline

Use these production settings on Brain:

- `GHOST_API_KEY` (required)
- `CORS_ORIGINS` (restrict to allowed origins)
- `MAX_REQUEST_BYTES` (guard large DOM payloads)

Client-side:

- Set `GHOST_API_KEY` in CI secrets.
- Never commit secrets into `ghost.yaml`.

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
