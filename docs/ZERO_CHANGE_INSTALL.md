# Zero-Change Install Guide

**Install SDK → run tests. No API key. No login. No secrets in project files.**

| Language | Guide |
|----------|-------|
| **Playwright TypeScript** | [PLAYWRIGHT_TS_USAGE.md](PLAYWRIGHT_TS_USAGE.md) |
| **JavaScript** | [JAVASCRIPT_USAGE.md](JAVASCRIPT_USAGE.md) |
| **Python** | [PYTHON_USAGE.md](PYTHON_USAGE.md) |
| **Java** | [JAVA_USAGE.md](JAVA_USAGE.md) |

---

## Quick commands

### TypeScript / JavaScript

```bash
npm install ghost-healer-ts-sdk
npx ghost-playwright test
```

### Python

```bash
pip install ghost-healer
pytest
```

### Java

```bash
# Add framework classes to test classpath — see JAVA_USAGE.md
mvn test
```

---

## What every SDK does automatically

- Connects to `https://ghost-healer-brain.onrender.com`
- Uses built-in SDK public key (no copy/paste from Render)
- Provisions `~/.ghost/credentials.json` on install / first run
- Intercepts locator failures and consults the AI Brain

---

## Healing flow (all languages)

| Run | Result |
|-----|--------|
| 1st | Locator may fail; failure recorded |
| After suite / runtime | Brain heals + patches source |
| 2nd | Test passes with healed locator |

---

## Optional overrides (enterprise only)

| Need | How |
|------|-----|
| Private Brain / custom key | `GHOST_API_KEY` in CI or `ghost-healer login` |
| Custom thresholds | `ghost.yaml` at project root |
