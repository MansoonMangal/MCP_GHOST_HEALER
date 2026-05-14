# 🛡️ Ghost Healer: Enterprise Usage Guidelines

Ghost Healer provides several modes of operation to balance safety and speed in production environments.

## ⚙️ Healing Modes

### 1. `runtime` (Default)
The framework heals the locator and continues execution immediately. Best for non-critical regression suites.
- **Auto-Patch**: Enabled (Source code is updated automatically).

### 2. `suggestion`
The framework does NOT heal automatically but logs the suggested locator in the report. Best for strict CI environments.
- **Auto-Patch**: Disabled.

### 3. `strict`
Only heals if the AI confidence score is above a specific threshold (e.g., 0.95). Otherwise, it fails the test.

## 📊 Analytics & Governance
Enterprise users can track:
- **Flakiness Reduction**: Number of tests saved from failing due to UI changes.
- **Maintenance ROI**: Calculated time saved on manual script updates.
- **Locator Stability**: Ranking of the most unstable parts of the application.

## 🏗️ Integration with CI/CD
To use Ghost Healer in your pipeline:
1. Ensure the `MCP_SERVER_URL` is set in your environment.
2. Initialize Ghost Healer using `ghost-healer init`.
3. The framework will automatically capture screenshots and DOM snapshots for any healed failure, making it easy to review in your CI logs.
