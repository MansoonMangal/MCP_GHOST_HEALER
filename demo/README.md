# 👻 Universal Ghost Healer: Multi-Language & Tool Integration Cheatsheet

Welcome to the **Practical Integration Report** for the **Universal Ghost Healer AI Self-Healing Platform**. This document acts as an immediate copy-paste cheatsheet to integrate, configure, and execute the self-healing framework across all **8 combinations** of the two leading automation tools (**Playwright & Selenium**) and the four core programming languages (**TypeScript, JavaScript, Python, and Java**).

---

## ⚙️ Core Configuration (`ghost.yaml`)

Regardless of the tool or language used, the framework is configured via a single centralized configuration file (`ghost.yaml`) placed in your project's workspace root:

```yaml
# ghost.yaml
mcp_server:
  url: "https://ghost-healer-brain.onrender.com"  # Live Centralized AI Brain URL
  confidence_threshold: -1.0                      # -1.0 dynamically auto-heals all decisions

healing:
  auto_patch: true                                # Dynamically patches test source files on disk
  max_retries: 3
  cooldown_ms: 1000
```

---

## 🚀 The 8 Integration Combinations

### 🟦 1. Playwright + TypeScript (`playwright-ts`)

#### 📂 File & Line to Change
* **Option A (Zero-Code Require Hook - Recommended)**: Simply prepend Node's require hook to your terminal execution command. No code edits are required!
* **Option B (Configuration Integration)**: Modify [playwright.config.ts](file:///c:/Users/mansoon.mangal.ASCENDION/OneDrive%20-%20ascendion/Desktop/API%20-%20My%20Work/MY%20PW_TS%20Project/playwright.config.ts) and add the global setup hook resolution:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // 👻 One-Line Prototype Injector
  globalSetup: require.resolve('ghost-healer-ts/dist/setup'),
  use: {
    headless: false,
    screenshot: 'only-on-failure',
  },
});
```

#### 💻 Execution Command
```bash
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/src/pw-hook.js" GHOST_CONFIG="ghost.yaml" npx playwright test tests/ui/e2e_checkout.spec.ts --project=chromium --headed
```

---

### 🟨 2. Playwright + JavaScript (`pw-js`)

#### 📂 File & Line to Change
* Prepend Node's require hook in your test script within `package.json`, or register the hook inside `playwright.config.js`:

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  // 👻 Global prototype interceptor
  globalSetup: require.resolve('ghost-healer-ts/dist/setup'),
  use: {
    headless: false,
  },
});
```

#### 💻 Execution Command
```bash
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/src/pw-hook.js" GHOST_CONFIG="ghost.yaml" npx playwright test
```

---

### 🐍 3. Playwright + Python (`playwright-python`)

#### 📂 File & Line to Change
Add a standard pytest fixture inside your `conftest.py` file to automatically wrap page objects with self-healing interceptors:

```python
# conftest.py
import pytest
from ghost_healer.adapters.playwright import protect_page

@pytest.fixture
def page(context):
    raw_page = context.new_page()
    # 👻 Dynamic Interceptor Activation
    protected_page = protect_page(raw_page)
    yield protected_page
    protected_page.close()
```

#### 💻 Execution Command
```bash
pytest --tb=short -v -s
```

---

### ☕ 4. Playwright + Java (`pw-java`)

#### 📂 File & Line to Change
Locate your JUnit or TestNG base setup file (e.g. `BaseTest.java`) where the `Page` object is instantiated:

```java
// src/test/java/demo/PlaywrightJavaDemo.java
package demo;

import com.microsoft.playwright.*;
import com.ghosthealer.core.GhostPlaywright;
import org.junit.jupiter.api.*;

public class PlaywrightJavaDemo {
    Page page;

    @BeforeEach
    void setUp() {
        Playwright playwright = Playwright.create();
        Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(false));
        BrowserContext context = browser.newContext();
        
        // 👻 ONE-LINE ACTIVATION: Wraps page with a self-healing dynamic proxy
        page = GhostPlaywright.protect(context.newPage());
    }
}
```

#### 💻 Execution Command
```bash
mvn clean test -Dtest=PlaywrightJavaDemo
```

---

### 🟦 5. Selenium + TypeScript (`selenium-ts`)

#### 📂 File & Line to Change
Inject the compiled selenium setup file globally into your test runner environment. In your terminal or `package.json` mocha command, append the `--require` flag:

```json
// package.json
"scripts": {
  "test:selenium": "cross-env GHOST_CONFIG=\"ghost.yaml\" ts-mocha --require ghost-healer-ts/selenium-setup tests/**/*.spec.ts"
}
```

#### 💻 Execution Command
```bash
npm run test:selenium
```

---

### 🟨 6. Selenium + JavaScript (`selenium-js`)

#### 📂 File & Line to Change
Similar to TypeScript, register the JavaScript Selenium setup script in your runner (Mocha/Jest) execution scripts in `package.json`:

```json
// package.json
"scripts": {
  "test:selenium-js": "cross-env GHOST_CONFIG=\"ghost.yaml\" mocha --require ghost-healer-ts/selenium-setup tests/**/*.spec.js"
}
```

#### 💻 Execution Command
```bash
npm run test:selenium-js
```

---

### 🐍 7. Selenium + Python (`selenium-python`)

#### 📂 File & Line to Change
Find your selenium driver instantiation class or fixtures (e.g., `conftest.py` or `webdriver_factory.py`) and wrap the webdriver instance immediately after creation:

```python
# conftest.py or test_file.py
import pytest
from selenium import webdriver
from ghost_healer.adapters.selenium import protect_driver

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    raw_driver = webdriver.Chrome(options=options)
    
    # 👻 ONE-LINE ACTIVATION: Intercepts all driver.find_element calls
    protect_driver(raw_driver)
    
    yield raw_driver
    raw_driver.quit()
```

#### 💻 Execution Command
```bash
pytest tests/selenium_suite.py
```

---

### ☕ 8. Selenium + Java (`selenium-java`)

#### 📂 File & Line to Change
Add the JUnit 5 healing extension (`@ExtendWith(GhostHealerExtension.class)`) to your Selenium test classes, and annotate the Selenium `WebDriver` field with `@GhostDriver`:

```java
// src/test/java/demo/SeleniumJavaDemo.java
package demo;

import com.ghosthealer.core.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;

@ExtendWith(GhostHealerExtension.class) // 👻 ACTIVATION STEP 1: Registers callback listeners
public class SeleniumJavaDemo {

    @GhostDriver // 👻 ACTIVATION STEP 2: Injects a dynamic self-healing proxy driver
    protected WebDriver driver;

    @BeforeEach
    void setUp() {
        driver = new ChromeDriver();
    }
}
```

#### 💻 Execution Command
```bash
mvn clean test -Dtest=SeleniumJavaDemo
```

---

## 📊 Self-Healing Output Logs & Reports

Whenever a locator is dynamically healed by Ghost Healer, the framework logs it in the following places:
1. **Audit Trail JSON** (`reports/ghost/suggested-fixes.json`): A clean, human-readable list showing exactly which broken selector failed, what exact healed locator replaced it, its confidence score, and the exact Page Object source file/line where it is defined.
2. **Dynamic Patches**: The source code is updated instantly in place, permanently resolving the maintenance overhead.

🛡️ **Stop fixing locators manually. Deploy Ghost Healer and let AI auto-heal your suites!** 🛡️
