# 🛡️ HealQA — AI-Powered Self-Healing Automation Framework

> Production-grade QA automation platform using **Playwright (Python) + MCP Architecture + AI DOM Analyzer**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/Playwright-Python-red?logo=playwright)](https://playwright.dev/python)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://react.dev)

---

## 🏗️ Architecture

```
Playwright Test (Python)
    ↓ locator fails
safe_click() / safe_fill() wrapper
    ↓ POST /heal-locator
MCP Server (FastAPI)
    ↓
Healing Service (Orchestrator)
    ├── Feature Extractor (parse selector)
    ├── DOM Analyzer (BeautifulSoup4 + lxml)
    ├── Similarity Engine (rapidfuzz weighted scoring)
    ├── Confidence Engine (AUTO_HEAL / MANUAL_REVIEW / FAIL)
    └── Locator Validator (uniqueness + interactivity check)
    ↓
Healed Locator returned to wrapper
    ↓ retry action
Test Passes ✅
    ↓
JSON Database + Logs
    ↓
React Dashboard (Real-time Analytics)
```

---

## 📁 Project Structure

```
MCP_CLIENT_SERVER_PROJECT/
├── mcp-server/              # Python FastAPI — AI healing engine
│   ├── main.py              # App entrypoint
│   ├── config/settings.py   # Config-driven (env vars)
│   ├── api/
│   │   ├── routes.py        # 4 enterprise REST APIs
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── healing_service.py     # 8-step orchestrator
│   │   ├── confidence_engine.py   # Threshold decision rules
│   │   └── locator_validator.py   # DOM validation
│   ├── ai_engine/
│   │   ├── dom_analyzer.py        # BS4 DOM parsing
│   │   ├── similarity_engine.py   # Weighted scoring (rapidfuzz)
│   │   └── feature_extractor.py   # Selector reverse-engineering
│   ├── utils/
│   │   ├── logger.py        # JSON structured logging
│   │   └── db_manager.py    # Thread-safe JSON persistence
│   └── database/            # JSON flat-file storage
│
├── mcp-client/              # Python Playwright tests
│   ├── wrappers/
│   │   ├── safe_locator.py  # Core healing wrapper
│   │   ├── safe_click.py    # Click wrapper
│   │   └── safe_fill.py     # Fill wrapper
│   ├── test-runner/
│   │   └── healing_reporter.py  # Pytest plugin
│   ├── playwright-tests/
│   │   ├── test_login.py    # Login healing demo
│   │   └── test_dashboard.py  # Dashboard healing demo
│   ├── conftest.py          # Global fixtures + plugin registration
│   └── pytest.ini           # Playwright pytest config
│
├── frontend/                # React 18 + Recharts Dashboard
│   └── src/components/
│       ├── Dashboard.tsx    # KPI overview
│       ├── ConfidenceChart.tsx   # Score distribution charts
│       ├── HealingHistory.tsx    # Filterable events table
│       ├── FailureHeatmap.tsx    # Unstable locator heatmap
│       └── ExecutionTimeline.tsx # Timeline by test
│
├── demo-app/                # HTML demo app (working + broken)
│   ├── index.html           # Working login (#email, #password, #login-btn)
│   ├── dashboard.html       # Working dashboard
│   └── broken-version/      # ← CHANGED locators trigger healing
│       ├── index.html       # #user-email, #user-password, #btn-submit
│       └── dashboard.html   # .btn-signout, #new-user-btn
│
└── reports/
    ├── logs/                # JSON healing reports per run
    └── screenshots/         # Playwright screenshots
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for React dashboard only)
- pip

---

### Step 1 — Install & Start MCP Server

```bash
cd mcp-server

# Copy env file
copy .env.example .env

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: **http://localhost:8000**
API Docs at: **http://localhost:8000/docs**

---

### Step 2 — Serve Demo App

```bash
# From project root — no install needed
npx http-server demo-app -p 3000 --cors
```

Demo app at: **http://localhost:3000**

---

### Step 3 — Run Playwright Tests (Python)

```bash
cd mcp-client

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Run all tests (with healing!)
pytest playwright-tests/ -v -s

# Run only login tests
pytest playwright-tests/test_login.py -v -s

# Run headless
pytest playwright-tests/ -v -s --headed=false
```

**Expected output:**
```
test_login_email_field_heals  → ✅ HEALED | '#email' → '#user-email' | Score: 89.3 | HIGH
test_login_password_field_heals → ✅ HEALED | '#password' → '#user-password' | Score: 87.1 | HIGH
test_login_button_heals       → ✅ HEALED | '#login-btn' → '#btn-submit' | Score: 91.2 | HIGH
```

---

### Step 4 — Start React Dashboard

```bash
cd frontend

npm install
npm run dev
```

Dashboard at: **http://localhost:5173**

---

## 🔌 MCP Server APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/heal-locator` | Main healing pipeline |
| `GET` | `/healing-history` | All healing records (filterable) |
| `GET` | `/confidence-report` | Aggregated analytics |
| `GET` | `/execution-trace/{id}` | Full decision trace |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |

### POST /heal-locator — Example Request

```json
{
  "original_locator": "#login-btn",
  "dom_snapshot": "<html>...</html>",
  "failure_reason": "TimeoutError: locator not found within 3000ms",
  "page_url": "http://localhost:3000/broken-version/index.html",
  "action": "click",
  "test_name": "test_login_button_heals",
  "element_hints": { "text": "Login", "tag": "button" }
}
```

### POST /heal-locator — Example Response

```json
{
  "healing_id": "a1b2c3d4-...",
  "original_locator": "#login-btn",
  "healed_locator": "#btn-submit",
  "confidence_score": 91.2,
  "confidence_level": "HIGH",
  "decision": "AUTO_HEAL",
  "candidates": [
    {
      "locator": "#btn-submit",
      "score": 91.2,
      "confidence_level": "HIGH",
      "score_breakdown": {
        "text_similarity": 100.0,
        "attribute_similarity": 72.3,
        "dom_structure_similarity": 95.0,
        "semantic_role_similarity": 100.0,
        "visibility_score": 100.0,
        "final_score": 91.2
      }
    }
  ],
  "execution_trace": {
    "steps": [
      {"step": 1, "name": "Feature Extraction", "status": "OK"},
      {"step": 2, "name": "DOM Analysis", "status": "OK", "detail": "Scanned 12 elements"},
      {"step": 3, "name": "Similarity Ranking", "status": "OK", "detail": "Top score: 91.2"},
      {"step": 4, "name": "Confidence Evaluation", "status": "OK", "detail": "AUTO_HEAL approved"},
      {"step": 5, "name": "Locator Validation", "status": "OK"}
    ]
  }
}
```

---

## 🧠 Similarity Engine Weights

```
final_score = (text_similarity   × 0.35)
            + (attribute_sim     × 0.25)
            + (dom_structure     × 0.20)
            + (semantic_role     × 0.10)
            + (visibility_score  × 0.10)
```

All weights are configurable via environment variables.

---

## ⚙️ Configuration (.env)

```env
AUTO_HEAL_THRESHOLD=85.0       # Score >= 85 → AUTO_HEAL
MANUAL_REVIEW_THRESHOLD=60.0   # Score 60-84 → MANUAL_REVIEW, < 60 → FAIL
WEIGHT_TEXT_SIMILARITY=0.35
WEIGHT_ATTRIBUTE_SIMILARITY=0.25
WEIGHT_DOM_STRUCTURE=0.20
WEIGHT_SEMANTIC_ROLE=0.10
WEIGHT_VISIBILITY=0.10
LOG_LEVEL=INFO
```

---

## 📊 Dashboard Features

| View | What It Shows |
|------|--------------|
| **Overview** | KPI cards: total events, success rate, avg score, manual reviews |
| **Confidence Charts** | Score distribution bar chart + confidence level pie chart |
| **Healing History** | Filterable table of all healing events with breakdown side panel |
| **Failure Heatmap** | Most unstable locators ranked by failure frequency |
| **Execution Timeline** | Events grouped by test with visual timeline |

---

## 🔥 What Gets Demonstrated

1. Playwright test runs against **broken app** (locators changed)
2. `safe_fill("#email")` → TimeoutError caught by wrapper
3. DOM snapshot captured → `POST /heal-locator` called
4. AI engine parses DOM, extracts 12+ interactive elements
5. Similarity engine scores each: `#user-email` scores **89.3**
6. Confidence engine: `89.3 ≥ 85` → `AUTO_HEAL`
7. Locator validated → unique + interactable ✅
8. Test retries with `#user-email` → fill succeeds
9. Full trace + JSON log written to `reports/logs/`
10. Dashboard shows live healing event with score breakdown
