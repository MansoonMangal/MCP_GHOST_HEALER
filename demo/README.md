# 👻 Ghost Healer — All 8 Framework Demos

All demos use **intentionally broken locators**.
Ghost Healer heals them. Tests pass. You change as little as possible.

---

## Minimum Change Summary

| Framework | Language | Change in Test Files | One-Time Setup |
|-----------|----------|---------------------|----------------|
| Playwright | Python | ✅ **ZERO** | `pip install ghost-healer` |
| Playwright | TypeScript | ✅ **ZERO** | 1 line in `playwright.config.ts` |
| Playwright | JavaScript | ✅ **ZERO** | 1 line in `playwright.config.js` |
| Playwright | Java | ✅ **ZERO** | 1 line in `@BeforeEach` of BaseTest |
| Selenium | Python | ✅ **ZERO** | 1 fixture in `conftest.py` |
| Selenium | TypeScript | ✅ **ZERO** | 1 line in jest/mocha setup |
| Selenium | JavaScript | ✅ **ZERO** | 1 line in jest/mocha setup |
| Selenium | Java | ✅ **ZERO** | 2 annotations on BaseTest |

---

## 🐍 Playwright + Python
```bash
cd demo/playwright-python
pip install ghost-healer pytest-playwright
playwright install chromium
pytest test_demo.py -v -s
```
**Zero-code setup**: `pip install ghost-healer` auto-registers pytest plugin.

---

## 🟦 Playwright + TypeScript
```bash
cd demo/playwright-ts
npm install @playwright/test
npx playwright install chromium
GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com npx playwright test
```
**One-time setup**: `playwright.config.ts` → add `globalSetup: require.resolve('ghost-healer-ts/setup')`

---

## 🟨 Playwright + JavaScript
```bash
cd demo/pw-js
npm install @playwright/test
npx playwright install chromium
GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com npx playwright test
```
**One-time setup**: `playwright.config.js` → add `globalSetup: require.resolve('ghost-healer-ts/setup')`

---

## ☕ Playwright + Java
```xml
<!-- pom.xml — add these dependencies -->
<dependency>
  <groupId>com.microsoft.playwright</groupId>
  <artifactId>playwright</artifactId>
  <version>1.40.0</version>
</dependency>
```
```java
// BaseTest.java — ONE LINE CHANGE
page = GhostPlaywright.protect(context.newPage());
```
**Run**: `mvn test -Dtest=PlaywrightJavaDemo`

---

## 🐍 Selenium + Python
```bash
cd demo/selenium-python
pip install ghost-healer selenium
python test_demo.py
```
**One-time setup**: Add to `conftest.py`:
```python
@pytest.fixture(autouse=True)
def ghost_selenium(driver):
    from ghost_healer.adapters.selenium import protect_driver
    protect_driver(driver)
    yield
```

---

## 🟦 Selenium + TypeScript
```bash
cd demo/selenium-ts
npm install selenium-webdriver ts-mocha ghost-healer-ts
GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com \
  npx ts-mocha --require ghost-healer-ts/selenium-setup test_demo.spec.ts
```
**One-time setup**: `--require ghost-healer-ts/selenium-setup` in mocha opts.

---

## 🟨 Selenium + JavaScript
```bash
cd demo/selenium-js
npm install selenium-webdriver mocha ghost-healer-ts
GHOST_BRAIN_URL=https://ghost-healer-brain.onrender.com \
  npx mocha --require ghost-healer-ts/selenium-setup test_demo.spec.js
```

---

## ☕ Selenium + Java
```java
// BaseTest.java — TWO CHANGES ONLY:
@ExtendWith(GhostHealerExtension.class)   // ← Change 1
public class BaseTest {
    @GhostDriver                           // ← Change 2
    protected WebDriver driver;
}
```
**All test subclasses heal automatically. Run**: `mvn test -Dtest=SeleniumJavaDemo`

---

## 📊 After Running Any Demo
Check `reports/ghost/` for a JSON report showing:
- Which locators were broken and what they healed to
- Confidence score per heal
- Total healing time saved
