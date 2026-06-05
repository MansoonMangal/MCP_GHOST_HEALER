# Ghost Healer — Playwright TypeScript Usage

**Install SDK → run tests. No API key. No login. No test file changes.**

---

## Step 1 — Install (once per project)

In your Playwright project root:

```bash
npm install ghost-healer-ts-sdk@1.2.2
```

On install the SDK automatically:

- Adds `NODE_OPTIONS=--require ghost-healer-ts-sdk/auto-activate` to `.env`
- Provisions Brain access (built-in SDK key — no copy/paste)
- Injects Playwright hooks + `globalSetup` / `globalTeardown`

**You do not edit `playwright.config.ts`.**

---

## Step 2 — Run tests (unchanged scripts)

Use either command — both activate Ghost:

```bash
npx playwright test
```

```bash
npx ghost-playwright test
```

`ghost-playwright` is a thin wrapper that ensures `NODE_OPTIONS` is set even if `.env` was not loaded yet. Recommended in `package.json` scripts:

```json
{
  "scripts": {
    "test": "ghost-playwright test",
    "test:ui": "ghost-playwright test tests/ui --headed"
  }
}
```

---

## Step 3 — Verify (optional)

```bash
npx ghost-healer doctor
```

Expected:

```text
Access     : SDK built-in (install-only)
API key    : configured ✓
Brain      : healthy ✓
```

---

## What you never change

| File | Action |
|------|--------|
| Test specs (`.spec.ts`) | **No edits** |
| Page objects | **No edits** |
| `playwright.config.ts` | **No edits** |
| Locator wrappers | **Not needed** |

Write normal Playwright tests with standard locators (`page.locator('#id')`, `getByRole`, etc.).

---

## How healing works

```text
Run 1  →  Locator fails (e.g. #address changed on site)
         →  Failure recorded during test run
After suite  →  Ghost calls AI Brain, patches your source file
Run 2  →  Healed locator used → test passes
```

Console markers:

```text
[GHOST] auto-activate: Playwright hooks loaded
[GHOST] 👻 Ghost Healer activated — Deferred Parallel Healing mode.
[GHOST] 🧠 Consulting AI Brain for N failure(s)...
[GHOST] ✅ Patched: tests/...
```

---

## Project `.env` (optional)

Only app URLs — **not** Ghost secrets:

```env
BASE_URL=https://automationexercise.com
API_BASE_URL=https://automationexercise.com/api
NODE_OPTIONS=--require ghost-healer-ts-sdk/auto-activate
```

Do not commit `.env` to git.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Cannot find module './credentials'` | Upgrade to `ghost-healer-ts-sdk@1.2.2+` and remove any manual `node_modules` patch |
| No `[GHOST]` logs | Run `npx ghost-playwright test` or confirm `NODE_OPTIONS` in `.env` |
| 401 from Brain | Redeploy Brain from latest repo (accepts SDK public key) |
| Test fails twice | Check `npx ghost-healer doctor`; confirm Brain is healthy |

---

## Upgrade from 1.2.0 / 1.2.1

```bash
npm install ghost-healer-ts-sdk@1.2.2
```

Remove any project-level workaround that copied `credentials.js` into `node_modules` — not needed from 1.2.2 onward.

---

## CI/CD (GitHub Actions example)

```yaml
- run: npm ci
- run: npx ghost-playwright test
```

No secrets required for the hosted Brain. For a private Brain, set `GHOST_API_KEY` as a CI secret.
