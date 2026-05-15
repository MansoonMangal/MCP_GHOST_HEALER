# 👻 Ghost Healer — Demo Projects

These demos prove that Ghost Healer heals broken locators **invisibly** at runtime.
Each demo uses **intentionally wrong locators**. Ghost intercepts every failure,
calls the AI Brain, and completes the action with the correct element.

---

## 🧪 Demo 1: Playwright Python

```bash
cd demo/playwright-python
pip install ghost-healer playwright pytest-playwright
playwright install chromium
pytest test_demo.py -v -s
```

**What happens**: `#user-name-WRONG`, `#password-WRONG`, and `#login-btn-WRONG`
all fail, Ghost heals each one, login succeeds. ✅

---

## 🧪 Demo 2: Playwright TypeScript

```bash
cd demo/playwright-ts
npm install
GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com npx playwright test
```

**What happens**: `GhostLocator.fill()` and `GhostLocator.click()` call the AI Brain
to heal broken selectors before retrying. ✅

---

## 🧪 Demo 3: Selenium Python

```bash
cd demo/selenium-python
pip install ghost-healer selenium
python test_demo.py
```

**What happens**: `protect_driver()` wraps `find_element`. Broken IDs are healed
by the AI before Selenium retries the action. ✅

---

## 📊 After Running

Check `reports/ghost/` for a structured JSON report showing:
- Which locators were broken
- What they were healed to
- Confidence score for each heal
- Total time saved
