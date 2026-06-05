# Ghost Healer — Python Usage (Playwright + Selenium)

**Install SDK → run pytest. No API key. No login. No test file changes.**

---

## Step 1 — Install (once per project / venv)

```bash
pip install ghost-healer
```

On install the SDK automatically:

- Provisions Brain access (`~/.ghost/credentials.json` with built-in SDK key)
- Registers the pytest plugin (`ghost`) via entry point

---

## Step 2 — Run tests (unchanged)

```bash
pytest
```

**You do not edit test files** for standard pytest setups.

### What auto-activates

| Framework | How |
|-----------|-----|
| **Playwright** | Pytest plugin auto-wraps the `page` fixture |
| **Selenium** | Pytest plugin auto-wraps `driver`, `browser`, `webdriver` fixtures |

---

## Step 3 — Verify (optional)

```bash
ghost-healer doctor
```

Expected:

```text
Access: SDK built-in (install-only)
API key: configured
Brain health: healthy
```

---

## What you never change

| Item | Change? |
|------|---------|
| Test files | No |
| `conftest.py` | No (plugin auto-loads) |
| API key / login | No |
| Locator wrappers | No |

Write normal Playwright/Selenium tests:

```python
def test_checkout(page):
    page.goto("https://example.com")
    page.locator("#submit").click()
```

---

## Healing flow

| Run | Result |
|-----|--------|
| 1st | Locator may fail — failure recorded |
| After suite | Brain heals + patches source |
| 2nd | Test passes |

---

## Optional `ghost.yaml`

Not required. Use for custom thresholds or healing mode:

```yaml
healing:
  mode: runtime
  auto_patch: true
mcp_server:
  confidence_threshold: 0.5
```

---

## CI/CD

```yaml
- run: pip install ghost-healer
- run: pytest
```

No secrets required for the hosted Brain.

---

## Optional overrides (enterprise)

| Need | How |
|------|-----|
| Private Brain | `ghost-healer login` or `GHOST_API_KEY` env |
| Disable autoload | `GHOST_AUTO_ACTIVATE=0` |
