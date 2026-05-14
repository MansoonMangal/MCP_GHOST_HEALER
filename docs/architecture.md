# 🏛️ Ghost Healer: Enterprise Architecture

Ghost Healer is designed as a distributed, language-agnostic platform for AI-powered automation maintenance.

## 🧩 Component Overview

### 1. The Ghost SDK (`ghost_healer`)
The client-side library that wraps automation drivers (Playwright, Selenium). 
- **Adapters**: Concrete implementations for different tools.
- **Healing Engine**: Intercepts failures and orchestrates the recovery flow.
- **Local Cache**: SQLite-based persistence to avoid redundant AI calls.

### 2. The AI Brain (`mcp-server`)
A centralized FastAPI service that performs the heavy lifting.
- **DOM DNA Matcher**: Uses structural analysis to find shifted elements.
- **LLM Integration**: Optional deep analysis for semantic changes.
- **Analytics Engine**: Stores healing trends and confidence scores.

## 🔄 The Healing Lifecycle

1. **Failure Detection**: The adapter catches a `TimeoutError`.
2. **Cache Check**: The SDK checks if a healed locator exists in SQLite.
3. **State Capture**: If not in cache, the SDK captures the DOM and stack trace.
4. **AI Analysis**: The Brain analyzes the state and returns a new locator.
5. **Execution**: The SDK performs the action with the healed locator.
6. **Persistence**:
   - **Local**: SQLite cache is updated.
   - **Source**: (Optional) The test script is patched with the new locator.
7. **Reporting**: A JSON execution trace is saved.

## 🚀 Scalability & Deployment
- **Horizontal Scaling**: The Brain is stateless and can be deployed in a K8s cluster.
- **Storage**: Supports SQLite (local) and MongoDB (centralized) for caching.
- **Communication**: gRPC or RESTful API.
