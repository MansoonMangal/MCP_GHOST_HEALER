# Ghost Healer 5-Minute Quickstart

Get self-healing running with zero test-script edits.

## 1) Install SDK

From project root:

```bash
pip install .
```

## 2) Configure Brain

Create/update `ghost.yaml`:

```yaml
mcp_server:
  url: "https://ghost-healer-brain.onrender.com"
  protocol: "mcp-first"
  confidence_threshold: 0.5
```

Use local Brain instead (optional):

```bash
cd mcp-server
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

Then set:

```bash
export GHOST_BRAIN_URL="http://127.0.0.1:8000"
```

## 3) Run Existing Tests (No Code Changes)

```bash
pytest -v
```

The pytest plugin auto-activates protection for:

- Playwright `page` fixture
- Selenium fixtures (`driver`, `browser`, `webdriver`, `selenium_driver`)

## 4) Verify Setup

```bash
ghost-healer doctor
ghost-healer report
```

If you use `suggestion` or `approval` mode:

```bash
ghost-healer review
```

## 5) Confirm Healing

Break a locator in any existing UI test and run again.

Expected behavior:

1. Failure is intercepted.
2. Brain returns healed candidate.
3. In `runtime`, test retries with healed locator (and may patch source if enabled).
4. Event appears in `reports/ghost/suggested-fixes.json`.
5. In non-runtime modes, item goes to `reports/ghost/pending-fixes.json`.
