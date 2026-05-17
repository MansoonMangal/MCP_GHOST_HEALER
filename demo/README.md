# 👻 Universal Ghost Healer: Multi-Language & Tool Integration Cheatsheet

Welcome to the **Practical Integration Report** for the **Universal Ghost Healer AI Self-Healing Platform**. This document is a complete, step-by-step, self-contained guide designed to help you download the SDK, integrate the configuration, and run the self-healing framework across all **8 combinations** of the two leading automation tools (**Playwright & Selenium**) and the four core programming languages (**TypeScript, JavaScript, Python, and Java**).

---

## ⚙️ Core Configuration (`ghost.yaml`)

Regardless of the tool or language used, the framework is configured via a single centralized configuration file named `ghost.yaml`. 

### Step 1: Create the Configuration File
Create a file named `ghost.yaml` in the **root directory** of your automation project:

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

## 🚀 The 8 Integration Combinations (Step-by-Step)

---

### 🟦 1. Playwright + TypeScript

Follow these steps to integrate Ghost Healer into a standard TypeScript Playwright framework:

#### Step 1: Install the SDK Package
Install the TypeScript self-healing package via npm:
```bash
npm install ghost-healer-ts --save-dev
```

#### Step 2: Add to Configuration
Open your standard configuration file (`playwright.config.ts`) and add the global setup hook registration:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // 👻 Registers the global prototype self-healing setup
  globalSetup: require.resolve('ghost-healer-ts/dist/setup'),
  use: {
    headless: false,
    screenshot: 'only-on-failure',
  },
});
```

#### Step 3: Run Your Tests
Execute your Playwright test commands as you normally would, prepending the `GHOST_CONFIG` environment variable:
```bash
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/src/pw-hook.js" GHOST_CONFIG="ghost.yaml" npx playwright test
```

---

### 🟨 2. Playwright + JavaScript

Follow these steps to integrate Ghost Healer into a standard JavaScript Playwright framework:

#### Step 1: Install the SDK Package
Install the JavaScript self-healing package via npm:
```bash
npm install ghost-healer-ts --save-dev
```

#### Step 2: Add to Configuration
Open your standard config file (`playwright.config.js`) and add the global setup hook:

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  // 👻 Global prototype interceptor registration
  globalSetup: require.resolve('ghost-healer-ts/dist/setup'),
  use: {
    headless: false,
  },
});
```

#### Step 3: Run Your Tests
Prepend Node's require hook and configuration path to your standard playwright command:
```bash
npx cross-env NODE_OPTIONS="-r ghost-healer-ts/src/pw-hook.js" GHOST_CONFIG="ghost.yaml" npx playwright test
```

---

### 🐍 3. Playwright + Python

Follow these steps to integrate Ghost Healer into a standard Python Playwright framework running `pytest`:

#### Step 1: Install the Python SDK
Install the python self-healing library via pip:
```bash
pip install ghost-healer
```

#### Step 2: Add to pytest Fixtures
Open your standard `conftest.py` file (located in your test root or `tests/` directory) and register the dynamic `page` interceptor:

```python
# tests/conftest.py
import pytest
from ghost_healer.adapters.playwright import protect_page

@pytest.fixture
def page(context):
    # Create the standard Playwright page instance
    raw_page = context.new_page()
    
    # 👻 Wraps the page instance with the AI self-healing interceptor
    protected_page = protect_page(raw_page)
    
    yield protected_page
    protected_page.close()
```

#### Step 3: Run Your Tests
Simply run your `pytest` suite normally. The adapter will catch any locator failures and dynamically heal them:
```bash
pytest -v -s
```

---

### ☕ 4. Playwright + Java

Follow these steps to integrate Ghost Healer into a standard Java Playwright project running Maven or Gradle:

#### Step 1: Download and Add dependencies
If using Maven, add the standard self-healing client dependency in your `pom.xml`:
```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.ghosthealer</groupId>
    <artifactId>ghost-healer-core</artifactId>
    <version>1.0.0</version>
</dependency>
```
*(Alternatively, copy the dynamic classes `GhostPlaywright.java`, `GhostHealerExtension.java`, and `GhostDriver.java` directly into your workspace at `src/main/java/com/ghosthealer/core/`)*

#### Step 2: Modify Your Page Instantiation
Locate your standard base setup file (e.g., `src/test/java/com/example/BaseTest.java` or where you instantiate the Playwright `Page` object) and wrap the newly created page instance:

```java
// src/test/java/com/example/BaseTest.java
package com.example;

import com.microsoft.playwright.*;
import com.ghosthealer.core.GhostPlaywright;
import org.junit.jupiter.api.*;

public class BaseTest {
    protected Page page;

    @BeforeEach
    void setUp() {
        Playwright playwright = Playwright.create();
        Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(false));
        BrowserContext context = browser.newContext();
        
        // 👻 ONE-LINE INTERCEPTION: Wraps the default page with a dynamic self-healing proxy
        page = GhostPlaywright.protect(context.newPage());
    }
}
```

#### Step 3: Run Your Tests
Execute your standard JUnit/TestNG test runners:
```bash
mvn clean test
```

---

### 🟦 5. Selenium + TypeScript

Follow these steps to integrate Ghost Healer into a standard Selenium framework running TypeScript and Mocha/Jest:

#### Step 1: Install the SDK Package
Install the TS/JS self-healing library:
```bash
npm install ghost-healer-ts --save-dev
```

#### Step 2: Modify Execution Command / Scripts
Open your project's `package.json` file and append the global require hook register command:

```json
// package.json
"scripts": {
  "test:selenium": "cross-env GHOST_CONFIG=\"ghost.yaml\" ts-mocha --require ghost-healer-ts/selenium-setup tests/**/*.spec.ts"
}
```

#### Step 3: Run Your Tests
Execute the configured runner:
```bash
npm run test:selenium
```

---

### 🟨 6. Selenium + JavaScript

Follow these steps to integrate Ghost Healer into a standard Selenium framework running JavaScript and Mocha/Jest:

#### Step 1: Install the SDK Package
Install the TS/JS self-healing library:
```bash
npm install ghost-healer-ts --save-dev
```

#### Step 2: Register Setup Script in Runner
Append the `--require` setup script parameters in your package scripts:

```json
// package.json
"scripts": {
  "test:selenium-js": "cross-env GHOST_CONFIG=\"ghost.yaml\" mocha --require ghost-healer-ts/selenium-setup tests/**/*.spec.js"
}
```

#### Step 3: Run Your Tests
Execute the script:
```bash
npm run test:selenium-js
```

---

### 🐍 7. Selenium + Python

Follow these steps to integrate Ghost Healer into a standard Selenium framework running Python and pytest:

#### Step 1: Install the Python SDK
Install the python self-healing library:
```bash
pip install ghost-healer
```

#### Step 2: Wrap Webdriver Instantiation
Open your shared setup file (e.g. `tests/conftest.py` or your custom webdriver factory) and wrap the standard driver instance immediately after creation:

```python
# tests/conftest.py
import pytest
from selenium import webdriver
from ghost_healer.adapters.selenium import protect_driver

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    raw_driver = webdriver.Chrome(options=options)
    
    # 👻 ONE-LINE ACTIVATION: Intercepts all driver.find_element actions globally
    protect_driver(raw_driver)
    
    yield raw_driver
    raw_driver.quit()
```

#### Step 3: Run Your Tests
Execute pytest to run your selenium suite:
```bash
pytest tests/
```

---

### ☕ 8. Selenium + Java

Follow these steps to integrate Ghost Healer into a standard Java Selenium project running JUnit 5:

#### Step 1: Download and Add dependencies
If using Maven, add the standard self-healing client dependency in your `pom.xml`:
```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.ghosthealer</groupId>
    <artifactId>ghost-healer-core</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### Step 2: Add Extension and Annotations
Modify your base Selenium test class (e.g., `src/test/java/com/example/BaseSeleniumTest.java`). Register the JUnit 5 self-healing callback listener and annotate your driver field:

```java
// src/test/java/com/example/BaseSeleniumTest.java
package com.example;

import com.ghosthealer.core.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;

@ExtendWith(GhostHealerExtension.class) // 👻 STEP 1: Registers the self-healing driver listener callbacks
public class BaseSeleniumTest {

    @GhostDriver // 👻 STEP 2: Automatically injects the dynamic self-healing proxy driver at runtime
    protected WebDriver driver;

    @BeforeEach
    void setUp() {
        driver = new ChromeDriver();
    }
}
```

#### Step 3: Run Your Tests
Execute your suite with Maven:
```bash
mvn clean test
```

---

## 📊 Self-Healing Output Logs & Reports

Whenever a locator is dynamically healed by Ghost Healer, the framework logs it in the following places:
1. **Audit Trail JSON** (`reports/ghost/suggested-fixes.json`): A clean, human-readable list showing exactly which broken selector failed, what exact healed locator replaced it, its confidence score, and the exact Page Object source file/line where it is defined.
2. **Dynamic Patches**: The source code is updated instantly in place, permanently resolving the maintenance overhead.

🛡️ **Stop fixing locators manually. Deploy Ghost Healer and let AI auto-heal your suites!** 🛡️
