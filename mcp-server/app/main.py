"""
Ghost Healer AI Brain — FastAPI Entry Point (Production)

Delegates all healing logic to the real AI pipeline:
  services/healing_service.py → ai_engine/ → similarity_engine
"""
import sys
import os
import time
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Make sure sibling packages (services/, ai_engine/, etc.) are importable ──
# When deployed via Docker, WORKDIR=/app/mcp-server, so this resolves correctly.
_server_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _server_root not in sys.path:
    sys.path.insert(0, _server_root)

from services.healing_service import heal
from utils.db_manager import get_confidence_report_data, _ensure_db_files
from utils.logger import get_logger
from config.settings import settings

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ghost Healer AI Brain",
    version="3.0.0",
    description="Universal AI Self-Healing Middleware for Automation Frameworks",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("fastapi_brain", settings.log_file, settings.log_level)
_ensure_db_files()

# ── Request / Response schemas ─────────────────────────────────────────────────

class HealRequest(BaseModel):
    selector: str
    action: str = "click"
    dom_snapshot: str
    page_url: Optional[str] = ""
    test_name: Optional[str] = None
    failure_reason: Optional[str] = "element_not_found"
    element_hints: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

class ScoreBreakdown(BaseModel):
    text_similarity: float = 0.0
    attribute_similarity: float = 0.0
    dom_structure_similarity: float = 0.0
    semantic_role_similarity: float = 0.0
    visibility_score: float = 0.0
    final_score: float = 0.0

class HealResponse(BaseModel):
    healing_id: str
    healed_locator: Optional[str]
    confidence: float
    confidence_level: str          # HIGH / MEDIUM / LOW
    decision: str                  # AUTO_HEAL / MANUAL_REVIEW / FAIL
    analysis: str
    score_breakdown: Optional[Dict[str, Any]] = None
    candidates_evaluated: int = 0
    latency_ms: float

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "engine": "real-dna-matcher",
        "auto_heal_threshold": settings.auto_heal_threshold,
    }

@app.post("/api/heal-locator", response_model=HealResponse)
async def heal_locator(request: HealRequest):
    """
    Main healing endpoint. Runs the full AI pipeline:
    1. Feature extraction from selector
    2. DOM candidate analysis
    3. Weighted similarity scoring
    4. Confidence evaluation
    5. Locator validation
    """
    start = time.time()
    logger.info(
        f"Heal request | selector={request.selector} | action={request.action}"
        f" | test={request.test_name}"
    )

    try:
        result = heal(
            original_locator=request.selector,
            dom_snapshot=request.dom_snapshot,
            failure_reason=request.failure_reason or "element_not_found",
            page_url=request.page_url or "",
            action=request.action,
            test_name=request.test_name,
            element_hints=request.element_hints,
        )
    except Exception as exc:
        logger.error(f"Healing pipeline error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

    latency = (time.time() - start) * 1000

    # Build analysis summary from execution trace
    steps = result.get("execution_trace", {}).get("steps", [])
    analysis = steps[-1]["detail"] if steps else result.get("decision", "No analysis available")

    # Score breakdown from best candidate
    best_candidates = result.get("candidates", [])
    breakdown = best_candidates[0].get("score_breakdown", {}) if best_candidates else {}

    return HealResponse(
        healing_id=result["healing_id"],
        healed_locator=result.get("healed_locator"),
        confidence=round(result.get("confidence_score", 0.0) / 100, 4),  # normalize 0-1
        confidence_level=result.get("confidence_level", "LOW"),
        decision=result.get("decision", "FAIL"),
        analysis=analysis,
        score_breakdown=breakdown,
        candidates_evaluated=result.get("candidates_evaluated", 0),
        latency_ms=round(latency, 2),
    )

@app.get("/api/confidence-report")
def confidence_report():
    """Aggregated healing analytics."""
    try:
        data = get_confidence_report_data()
        return data
    except Exception as e:
        logger.warning(f"Report data error: {e}")
        return {"message": "No report data yet. Run some tests first."}

@app.get("/api/health")
def api_health():
    """Alias for health — for SDK backwards compatibility."""
    return health()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
