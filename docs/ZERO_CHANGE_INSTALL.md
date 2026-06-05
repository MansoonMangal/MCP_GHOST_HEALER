# Zero-Change Install Guide

**Goal:** `npm install` → `npx playwright test` — **no API key, no login, no config edits**.

---

## TypeScript / JavaScript (Playwright + Selenium)

```bash
npm install ghost-healer-ts-sdk
npx playwright test
```

That's it. The SDK:

- Enables auto-healing via `NODE_OPTIONS` in `.env` (on install)
- Connects to the hosted Brain with a **built-in SDK access key**
- Patches Playwright hooks + globalSetup/teardown automatically

Optional verify:

```bash
npx ghost-healer doctor
```

---

## Python (Playwright + Selenium)

```bash
pip install ghost-healer
pytest
```

Built-in Brain access — same install-only model.

---

## Java

```bash
mvn test
```

Uses built-in SDK access when `ghost-healer` JAR is on the classpath (no env vars required for hosted Brain).

---

## Optional overrides (enterprise only)

| Need | Command |
|------|---------|
| Private Brain / custom key | `npx ghost-healer login` or `GHOST_API_KEY` in CI |
| Custom thresholds | `ghost.yaml` at project root |

---

## Healing flow

| Run | Result |
|-----|--------|
| 1st | Locator may fail; failure recorded |
| After suite | Brain heals + patches source |
| 2nd | Test passes with healed locator |

Brain URL: `https://ghost-healer-brain.onrender.com`
