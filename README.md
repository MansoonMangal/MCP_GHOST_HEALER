# 👻 Ghost Healer: Universal AI Self-Healing Automation

### **The world's first language-agnostic, zero-refactor AI self-healing automation platform.**

Ghost Healer is a revolutionary framework that automatically detects broken locators during test execution, consults an AI Brain to find the correct element, and **permanently patches your source code** so you never have to fix the same locator twice.

---

## ✨ Key Features

- **Zero Code Changes Required**: Integrating Ghost Healer into your existing test suites requires absolutely no changes to your test scripts (`page.click()`, `driver.findElement()`, etc. remain untouched).
- **Cross-Platform & Cross-Language**: Fully supports **Playwright** and **Selenium** across **Python, Java, JavaScript, and TypeScript**.
- **Permanent Source Patching**: It doesn't just heal the test in memory; it finds your original source file and physically updates the code with the correct locator.
- **Cloud-Native Brain**: Connects to a centralized AI Brain (e.g., hosted on Render) for high-accuracy DOM analysis and element matching.

---

## 🚀 Quick Start Guide

### 1. Configure the Brain URL
Set the environment variable for the AI Brain.
```bash
export GHOST_BRAIN_URL="https://ghost-healer-brain.onrender.com"
```
*(On Windows PowerShell, use `$env:GHOST_BRAIN_URL="https://ghost-healer-brain.onrender.com"`)*

### 2. Integration by Platform

The beauty of Ghost Healer is the minimal setup required.

#### 🐍 Python (Playwright & Selenium)
**Setup**: Install the package.
```bash
pip install ghost-healer
```
**Playwright**: Run tests normally. The `pytest` plugin automatically wraps the `page` fixture.
```bash
pytest demo/playwright-python/test_demo.py
```
**Selenium**: Wrap your driver instance once.
```python
from ghost_healer import protect_driver
protect_driver(driver)
```

#### ☕ Java (Selenium & Playwright)
**Setup**: Add the dependency and extension.
**Selenium (JUnit 5)**: Add the `GhostHealerExtension` to your test class.
```java
@ExtendWith(GhostHealerExtension.class)
public class MyTest { ... }
```
**Playwright**: Use the `GhostHealer` wrapper around your Playwright `Page`.

#### 📜 JavaScript / TypeScript (Playwright & Selenium)
**Setup**: Install the package.
```bash
npm install ghost-healer-ts
```
**Playwright**: Add one line to your `playwright.config.ts`.
```typescript
globalSetup: require.resolve('ghost-healer-ts/dist/setup')
```
**Selenium**: Add one require statement to your test runner config (e.g., Mocha or Jest).
```javascript
// In .mocharc.js or jest.config.js
require('ghost-healer-ts/dist/selenium-setup')
```

---

## 🛠️ How It Works

1. **Interception**: When a locator fails (e.g., `NoSuchElementException` or Playwright Timeout), Ghost Healer intercepts the error.
2. **Analysis**: It captures the current DOM and sends it to the AI Brain.
3. **Healing**: The AI Brain analyzes the DOM, identifies the intended element, and returns a high-confidence updated locator.
4. **Execution**: Ghost Healer retries the action with the new locator, allowing the test to pass seamlessly.
5. **Patching**: Behind the scenes, the `SourceHealer` engine locates the exact file and line of code that failed and permanently updates it with the new locator.

---

**Stop fighting your locators. Start trusting your tests.** 🛡️🌍🏆✨
