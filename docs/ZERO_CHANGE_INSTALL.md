# Zero-Change Install Guide

**Goal:** Install SDK → **one-time login** → run tests **unchanged**.

No per-project `.env` API key editing. No edits to test files, page objects, or Playwright config.

---

## One-time setup (every developer machine)

Run **once** on your laptop or CI agent:

```bash
npx ghost-healer login          # TypeScript / Node projects
# or
ghost-healer login              # Python projects
```

Paste your team’s `GHOST_API_KEY` when prompted. Credentials are saved to:

```text
~/.ghost/credentials.json
```

All automation projects on that machine inherit the key automatically.

**Enterprise IT alternatives** (no login CLI needed):

| Method | Who sets it | Use case |
|--------|-------------|----------|
| `ghost-healer login --key=...` | IT script / onboarding | Bulk laptop setup |
| Machine env `GHOST_API_KEY` | IT / GPO / Intune | Windows/macOS/Linux fleet |
| CI secret `GHOST_API_KEY` | DevOps | GitHub Actions, Azure DevOps, Jenkins |

Never commit secrets. Do not put API keys in `ghost.yaml`.

---

## TypeScript / JavaScript (Playwright + Selenium)

```bash
npm install ghost-healer-ts-sdk
npx ghost-healer login    # once per machine
npx playwright test       # unchanged
```

**On `npm install`**, the SDK only merges auto-activation into `.env`:

```env
NODE_OPTIONS=--require ghost-healer-ts-sdk/auto-activate
```

It does **not** add `GHOST_API_KEY` to your project.

**What auto-activates (no config edits):**

- Playwright page/locator hooks (`pw-hook.js`)
- `globalSetup` / `globalTeardown` (deferred healing + source patch)
- Selenium `findElement` hooks (when `selenium-webdriver` is present)
- Credentials from `~/.ghost/credentials.json` or machine env

Optional `ghost.yaml` at project root for thresholds/modes — not required.

---

## Python (Playwright + Selenium)

```bash
pip install ghost-healer
ghost-healer login    # once per machine
pytest                # unchanged
```

Pytest plugin auto-wraps `page` and Selenium fixtures. Credentials + optional `.env` load automatically.

---

## Java (JUnit 5 + Selenium / Playwright)

Set machine or CI environment once:

```bash
export GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com
export GHOST_API_KEY=<team-key>
mvn test
```

Optional javaagent for zero-annotation mode — see [enterprise_usage.md](enterprise_usage.md).

---

## Verify

```bash
npx ghost-healer doctor   # Node
ghost-healer doctor       # Python
```

Brain URL: `https://ghost-healer-brain.onrender.com`

---

## What users never edit

| Do not change | Why |
|---------------|-----|
| Test scripts | Hooks intercept failures |
| Locator wrappers | Adapters patch at runtime |
| Playwright config (TS) | Auto-injected via `NODE_OPTIONS` + `defineConfig` patch |
| Project `.env` for API key | One-time `login` or IT-managed env var |

**Only manual step:** run `ghost-healer login` once (or IT sets `GHOST_API_KEY` fleet-wide).
