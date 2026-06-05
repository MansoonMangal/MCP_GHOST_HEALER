# Ghost Healer — JavaScript Usage (Playwright + Selenium)

JavaScript uses the **same npm package** as TypeScript: `ghost-healer-ts-sdk`.

**Install → run tests. No API key. No login. No test file changes.**

---

## Step 1 — Install

```bash
npm install ghost-healer-ts-sdk
```

On install the SDK:

- Adds `NODE_OPTIONS=--require ghost-healer-ts-sdk/auto-activate` to `.env`
- Provisions built-in Brain access automatically

---

## Step 2 — Run tests

```bash
npx playwright test
# or
npx ghost-playwright test
```

For Mocha/Jest + Selenium:

```bash
npx ghost-playwright test   # if using Playwright
# Selenium: NODE_OPTIONS is set by postinstall — run your test runner normally
npm test
```

Recommended `package.json` scripts:

```json
{
  "scripts": {
    "test": "ghost-playwright test"
  }
}
```

---

## Step 3 — Verify (optional)

```bash
npx ghost-healer doctor
```

---

## What you never change

| Item | Change? |
|------|---------|
| Test files (`.spec.js`) | No |
| `playwright.config.js` | No |
| API key / login | No |

---

## Full TypeScript guide

See [PLAYWRIGHT_TS_USAGE.md](PLAYWRIGHT_TS_USAGE.md) — identical flow for `.js` and `.ts` projects.
