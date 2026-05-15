# 👻 Ghost Healer: Tests That Fix Themselves
### **The world's first language-agnostic, zero-refactor AI self-healing automation platform.**

[![PyPI version](https://badge.fury.io/py/ghost-healer.svg)](https://badge.fury.io/py/ghost-healer)
[![Docker Support](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![Cloud Ready](https://img.shields.io/badge/deployment-cloud--ready-green.svg)](https://render.com)

---

## ☁️ Cloud-Native Reliability
Ghost Healer is now fully optimized for cloud deployments. Whether your AI Brain is hosted on **Render**, **AWS**, or **Azure**, the framework handles:
- **Automatic Wake-up**: Detects and waits for server "cold starts".
- **Resilient Connectivity**: Built-in exponential backoff for transient network issues.
- **SSL/HTTPS**: Production-ready encrypted communication.

---

## 🚀 Quick Start (Cloud Mode)

### 1. Configure the Brain
Update your `ghost.yaml` with your live Cloud Brain URL:
```yaml
mcp_server:
  url: "https://your-app.onrender.com"
```

### 2. Verify Connection
```bash
python scripts/verify_cloud.py
```

### 3. Run Protected Tests
```bash
pytest
```

---

## 🏛️ Project Architecture
Ghost Healer uses a **Distributed DNA Matching** architecture.

### 1. The SDK (`ghost_healer/`)
Installs in your test project. Invisible and zero-refactor.

### 2. The Brain (`mcp-server/`)
Centralized FastAPI server. Analyzes DOM snapshots and returns high-confidence heals. Now supports **Render Blueprint** for one-click global deployment.

---

**Stop fighting your locators. Start trusting your tests.** 🛡️🌍🏆✨
