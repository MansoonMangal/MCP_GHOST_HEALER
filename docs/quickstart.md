# ⏱️ Ghost Healer: 5-Minute Quickstart

Get your first self-healing automation script running in minutes.

## 1. Installation
```bash
pip install ghost-healer
```

## 2. Setup the Brain
Deploy the AI Brain using Docker:
```bash
cd mcp-server
docker-compose up -d
```

## 3. Bootstrap your Project
In your automation repository, run:
```bash
ghost-healer init
```
This will create:
- `ghost.yaml`: Central configuration.
- `conftest.py`: Automatic Playwright protection.
- `pytest.ini`: Standard testing config.

## 4. Write a Native Test
Create `tests/test_login.py`:
```python
def test_login(page):
    page.goto("https://example.com/login")
    
    # These standard locators will heal themselves if they break!
    page.fill("#username", "admin")
    page.fill("#password", "password123")
    page.click("button[type='submit']")
```

## 5. Execute
```bash
pytest
```

---

## 🔍 How to Verify?
To see healing in action, manually change an ID in your `test_login.py` to something wrong (e.g., `#username-wrong`). When you run `pytest`, Ghost Healer will:
1. Intercept the failure.
2. Find the correct element using AI.
3. Complete the login successfully.
4. **Rewrite your source code** to fix the locator permanently (if `auto_patch` is enabled in `ghost.yaml`).
