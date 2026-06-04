# Ghost Healer Architecture

Ghost Healer is a distributed, language-agnostic self-healing platform with an MCP-first Brain and multi-language SDK/adapters.

## Components

### 1) SDK and Adapters

- `ghost_healer/` (Python): pytest plugin, Playwright/Selenium adapters, CLI, cache.
- `sdk/ts/` (TS/JS): auto-activation hook, Playwright + Selenium runtime interception.
- `ghost_healer/framework/java/` (Java): client classes, JUnit 5 extension, optional javaagent.

Responsibilities:

- Detect locator failures.
- Capture DOM/page context.
- Call Brain (MCP REST shim first, legacy REST fallback).
- Retry and/or queue pending fixes depending on healing mode.

### 2) AI Brain (`mcp-server`)

FastAPI service with MCP gateway:

- MCP tools mount: `/mcp` (Streamable HTTP)
- MCP REST shim: `/api/mcp/v1/tools/{tool}`
- Legacy REST heal endpoint: `/api/heal-locator`

Core modules:

- `services/healing_service.py`: pipeline orchestration.
- `ai_engine/*`: DOM parsing + feature extraction + similarity scoring.
- `controllers/healing_controller.py`: shared API response shaping.
- `utils/db_manager.py`: JSON fallback or Mongo persistence.

### 3) Persistence and Reports

- Local/Dev storage (JSON files under `mcp-server/database/`).
- Production storage (MongoDB via `MONGO_URI`).
- SDK output under `reports/ghost/`:
  - `suggested-fixes.json`
  - `pending-fixes.json`
  - `session_*.json`

## Healing Lifecycle

1. SDK intercepts a locator failure.
2. SDK checks local cache (when enabled).
3. SDK sends selector + DOM to Brain.
4. Brain ranks candidates and decides `AUTO_HEAL` / `MANUAL_REVIEW` / `FAIL`.
5. SDK behavior by mode:
   - `runtime`: retry healed selector, optional source patch.
   - `suggestion`/`approval`: queue pending fix for review.
   - `strict`: accept only high-confidence heals.
6. Events and scores are persisted for analytics/feedback.

## Communication Contracts

- Confidence exposed to SDK/API consumers as `0.0..1.0`.
- Tenant/project context supported through:
  - `X-Ghost-Tenant`
  - `X-Ghost-Project`

## Deployment Model

- Stateless Brain container (Render-ready via `render.yaml`).
- Health endpoints:
  - `/health`
  - `/health/ready`
- Security:
  - API key support (`GHOST_API_KEY`)
  - payload size limit (`MAX_REQUEST_BYTES`)
