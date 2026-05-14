# 👻 Ghost Healer
### The Enterprise AI Self-Healing Automation Platform

Ghost Healer is a production-ready, language-agnostic platform that eliminates automation maintenance by healing broken locators in real-time.

[![CI](https://github.com/MansoonMangal/ghost-healer/actions/workflows/test.yml/badge.svg)](https://github.com/MansoonMangal/ghost-healer/actions)
[![PyPI version](https://badge.fury.io/py/ghost-healer.svg)](https://badge.fury.io/py/ghost-healer)

## 🚀 Quick Start

### 1. Install
```bash
pip install ghost-healer
```

### 2. Initialize
```bash
ghost-healer init
```

### 3. Start the Brain (Docker)
```bash
cd mcp-server
docker-compose up -d
```

### 4. Run your tests
```bash
pytest
```

---

## 🛠️ Key Features
- **Zero Refactor**: Works with your existing Playwright and Selenium scripts.
- **Permanent Fixes**: Automatically patches your source code with healed locators.
- **Intelligent Cache**: Reuses healed locators via a local SQLite layer.
- **Enterprise Ready**: Support for multiple healing modes (`runtime`, `suggestion`, `strict`).
- **Deep Analytics**: Rich dashboards showing confidence trends and ROI.

## 📖 Documentation
- [Architecture & Design](docs/architecture.md)
- [Enterprise Deployment](docs/enterprise_usage.md)
- [Deployment Guide](deployment_guide.md)

---

## 🌍 Language Support
| Language | Tool | Status |
|----------|------|--------|
| Python | Playwright | ✅ Stable |
| Python | Selenium | ✅ Stable |
| Java | Selenium | 🧪 Beta |
| TypeScript | Playwright | 🧪 Beta |

**Built for speed. Built for scale. Built for the Ghost.** 🛡️🌍🏆✨
