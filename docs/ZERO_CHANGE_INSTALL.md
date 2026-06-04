# Zero-Change Install Guide

Install the SDK for your language. **Do not edit test scripts.**

## Python (Playwright + Selenium)

```bash
pip install ghost-healer
pytest tests/
```

The pytest plugin auto-wraps `page` and common Selenium fixtures (`driver`, `browser`, `webdriver`).

## TypeScript / JavaScript (Playwright + Selenium)

```bash
npm install ghost-healer-ts
npx playwright test
# or: npx mocha / jest with selenium-webdriver
```

`postinstall` sets `NODE_OPTIONS=--require ghost-healer-ts/auto-activate`.

## Java (Playwright + Selenium)

Add `ghost-healer` JAR to test classpath. JUnit 5 auto-loads `GhostHealerExtension` via service loader.

Optional javaagent (wraps all `WebDriver` fields without `@GhostDriver`):

```bash
export JAVA_TOOL_OPTIONS="-javaagent:path/to/ghost-healer-agent.jar"
mvn test
```

## Brain URL

Default: `https://ghost-healer-brain.onrender.com`

Override: `GHOST_BRAIN_URL` or `ghost.yaml` → `mcp_server.url`

## Verify

```bash
ghost-healer doctor
```
