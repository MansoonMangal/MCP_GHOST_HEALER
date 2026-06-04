# Ghost Healer: Multi-Language Demo and Integration Guide

This guide shows how to run and integrate Ghost Healer across all **8 combinations**: **Playwright** and **Selenium** × **Python, TypeScript, JavaScript, Java**.

**Design goal:** install the SDK and run tests — **no edits to test scripts**. Use `ghost.yaml` and environment variables only.

---

## Prerequisites

- Python 3.10+ (for Python SDK and local Brain)
- Node.js 18+ (for TS/JS)
- Java 17+ and Maven (for Java demos under `demo/pw-java`)
- Optional: Chrome/Chromium for browser tests

---

## Core Configuration (`ghost.yaml`)

Create `ghost.yaml` in your **project root** (or the repo root when running demos from this repository):

```yaml
mcp_server:
  url: "https://ghost-healer-brain.onrender.com"
  timeout: 30
  confidence_threshold: 0.5
  protocol: "mcp-first"
  api_key: ""

healing:
  mode: "runtime"
  auto_patch: true
  cache_enabled: true
  max_retries: 3
  retry_wait_seconds: 5
  selenium_fixture_names:
    - driver
    - browser
    - webdriver
    - selenium_driver

reporting:
  output_dir: "reports/ghost"
  save_traces: true
```

Environment overrides:

| Variable | Purpose |
|----------|---------|
| `GHOST_BRAIN_URL` | Brain URL (overrides `mcp_server.url`) |
| `GHOST_API_KEY` | API key for secured Brain |
| `GHOST_CONFIG` | Path to alternate `ghost.yaml` |

Local Brain (optional):

```bash
cd mcp-server
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
# Then set GHOST_BRAIN_URL=http://127.0.0.1:8000
```

---

## Zero-Change vs Manual Wiring

| Approach | When to use |
|----------|-------------|
| **Zero-change (recommended)** | Install SDK; pytest plugin / npm postinstall / JUnit service loader handle activation |
| **Manual wiring** | Legacy projects or custom runners; examples below marked "optional" |

Full zero-change reference: [docs/ZERO_CHANGE_INSTALL.md](../docs/ZERO_CHANGE_INSTALL.md)

---

## Demo Paths in This Repo

| Combo | Demo folder / command |
|-------|------------------------|
| Playwright + Python | `demo/playwright-python/` |
| Playwright + TypeScript | `demo/playwright-ts/` |
| Playwright + JavaScript | `demo/pw-js/` |
| Playwright + Java | `demo/pw-java` → `mvn test -Dtest=PlaywrightJavaDemo` |
| Selenium + Python | `demo/selenium-python/` |
| Selenium + TypeScript | `demo/selenium-ts/` |
| Selenium + JavaScript | `demo/selenium-js/` |
| Selenium + Java | `demo/pw-java` → `mvn test -Dtest=SeleniumJavaDemo` |

From repository root:

```bash
pip install .
ghost-healer doctor
```

---

## 1. Playwright + TypeScript

### Install

```bash
cd demo/playwright-ts
npm install
# Link or install ghost-healer-ts from ../../sdk/ts (local) or npm registry
```

### Zero-change run

After `npm install ghost-healer-ts`, `postinstall` enables auto-activation. Run:

```bash
npx playwright test
```

### Optional explicit Playwright config

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: require.resolve('ghost-healer-ts/dist/setup'),
  globalTeardown: require.resolve('ghost-healer-ts/dist/teardown'),
  use: {
    actionTimeout: 10000,
  },
});
```

If hooks are not picked up automatically:

```bash
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/auto-activate" npx playwright test
```

---

## 2. Playwright + JavaScript

Same package as TypeScript (`ghost-healer-ts`).

```bash
cd demo/pw-js
npm install
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/auto-activate" npx playwright test
```

---

## 3. Playwright + Python

### Zero-change (recommended)

From repo root:

```bash
pip install .
pytest demo/playwright-python/test_demo.py -v -s
```

The `ghost` pytest plugin auto-protects the `page` fixture — **no `conftest.py` required**.

### Optional manual fixture

```python
# conftest.py — only if you disable the plugin
import pytest
from ghost_healer.adapters.playwright import protect_page

@pytest.fixture
def page(context):
    raw = context.new_page()
    yield protect_page(raw)
    raw.close()
```

---

## 4. Playwright + Java

```bash
cd demo/pw-java
mvn clean test -Dtest=PlaywrightJavaDemo
```

Ensure `ghost.yaml` is visible from the working directory or set `GHOST_BRAIN_URL`.

Optional: wrap page in base test with `GhostPlaywright.protect(page)` — see `ghost_healer/framework/java/GhostPlaywright.java`.

---

## 5. Selenium + TypeScript

```bash
cd demo/selenium-ts
npm install ghost-healer-ts
# Auto-activate via NODE_OPTIONS after install, or:
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/auto-activate" npm test
```

---

## 6. Selenium + JavaScript

```bash
cd demo/selenium-js
npm install ghost-healer-ts
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/auto-activate" npm test
```

---

## 7. Selenium + Python

### Zero-change (recommended)

```bash
pip install .
pytest demo/selenium-python/test_demo.py -v -s
```

Plugin auto-detects fixtures named `driver`, `browser`, `webdriver`, or `selenium_driver` (configurable in `ghost.yaml`).

### Optional manual wrap

```python
from ghost_healer.adapters.selenium import protect_driver

@pytest.fixture
def driver():
    d = webdriver.Chrome()
    protect_driver(d)
    yield d
    d.quit()
```

---

## 8. Selenium + Java

### Service loader (zero annotation on tests)

Place Ghost Healer JAR/classes on the test classpath. JUnit 5 loads `GhostHealerExtension` via:

`ghost_healer/framework/java/META-INF/services/org.junit.jupiter.api.extension.Extension`

```bash
cd demo/pw-java
mvn clean test -Dtest=SeleniumJavaDemo
```

### Optional javaagent (all `WebDriver` fields)

```bash
export JAVA_TOOL_OPTIONS="-javaagent:path/to/ghost-healer-agent.jar"
mvn clean test -Dtest=SeleniumJavaDemo
```

### Optional explicit annotations

```java
@ExtendWith(GhostHealerExtension.class)
public class BaseTest {
    @GhostDriver
    protected WebDriver driver;
}
```

---

## Healing Modes for Demos

| `healing.mode` | What you will see |
|----------------|-------------------|
| `runtime` | Test retries with healed locator; may patch source if `auto_patch: true` |
| `suggestion` | Heal logged; pending queue in `reports/ghost/pending-fixes.json` |
| `approval` | Same; use `ghost-healer review` from repo root |

---

## Reports and CLI

After a run:

| Output | Location |
|--------|----------|
| Suggested fixes | `reports/ghost/suggested-fixes.json` |
| Pending review | `reports/ghost/pending-fixes.json` |
| Session trace | `reports/ghost/session_*.json` |
| Brain logs | `reports/logs/mcp_server.log` (local Brain) |

```bash
ghost-healer doctor
ghost-healer report
ghost-healer review
ghost-healer review --approve-all
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Brain unreachable | Run `ghost-healer doctor`; check `GHOST_BRAIN_URL` and cold start on Render free tier |
| No healing in Python Selenium | Ensure fixture is named `driver` (or listed in `selenium_fixture_names`) |
| TS hooks not active | Confirm `NODE_OPTIONS` includes `ghost-healer-ts/auto-activate` |
| Java driver not wrapped | Add JAR to classpath or use `-javaagent` |
| 401 from Brain | Set `GHOST_API_KEY` to match Render env |

---

## Next Steps

- Main overview: [README.md](../README.md)
- MCP migration: [docs/MIGRATION_MCP_V1.md](../docs/MIGRATION_MCP_V1.md)
- Release gates: [release_checklist.md](../release_checklist.md)

Stop fixing locators manually — run the demos, then point your own suite at the same SDK and Brain.
