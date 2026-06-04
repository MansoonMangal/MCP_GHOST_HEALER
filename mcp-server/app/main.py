"""
Ghost Healer AI Brain — FastAPI + MCP (production entrypoint).
"""
import sys
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_server_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _server_root not in sys.path:
    sys.path.insert(0, _server_root)

from controllers import healing_controller as hc
from mcp_gateway.server import mcp, create_mcp_asgi_app
from middleware.auth import APIKeyMiddleware
from middleware.payload_limit import PayloadLimitMiddleware
from utils.db_manager import _ensure_db_files
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("fastapi_brain", settings.log_file, settings.log_level)
_ensure_db_files()

mcp_asgi = create_mcp_asgi_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
  async with mcp.session_manager.run():
    yield


app = FastAPI(
    title="Ghost Healer AI Brain",
    version="4.0.0",
    description="MCP-first universal self-healing brain with REST compatibility",
    lifespan=lifespan,
)

app.add_middleware(PayloadLimitMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", mcp_asgi)


# ── Schemas ───────────────────────────────────────────────────────────────────

class HealRequest(BaseModel):
    selector: str
    action: str = "click"
    dom_snapshot: str
    page_url: Optional[str] = ""
    test_name: Optional[str] = None
    failure_reason: Optional[str] = "element_not_found"
    element_hints: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class HealFeedbackRequest(BaseModel):
    healing_id: str
    accepted: bool
    reviewer: Optional[str] = None
    notes: Optional[str] = None


class PendingFixStatusRequest(BaseModel):
    status: str


class HealResponse(BaseModel):
    healing_id: str
    healed_locator: Optional[str]
    confidence: float
    confidence_level: str
    decision: str
    analysis: str
    score_breakdown: Optional[Dict[str, Any]] = None
    candidates_evaluated: int = 0
    latency_ms: float


class McpToolCallRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
@app.get("/api/health")
def health():
    return hc.get_health()


@app.get("/health/ready")
def readiness():
    data = hc.get_health()
    return {"ready": data.get("status") == "healthy", **data}


# ── REST (backward compatible) ────────────────────────────────────────────────

@app.post("/api/heal-locator", response_model=HealResponse)
async def heal_locator(request: HealRequest, http_req: Request):
    tenant_id = request_headers_tenant(http_req)
    project_id = request_headers_project(http_req)
    logger.info(
        f"Heal request | selector={request.selector} | action={request.action}"
        f" | test={request.test_name}"
    )
    try:
        result = hc.run_heal_locator(
            selector=request.selector,
            dom_snapshot=request.dom_snapshot,
            action=request.action,
            page_url=request.page_url or "",
            test_name=request.test_name,
            failure_reason=request.failure_reason or "element_not_found",
            element_hints=request.element_hints,
            tenant_id=tenant_id,
            project_id=project_id,
        )
    except Exception as exc:
        logger.error(f"Healing pipeline error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return HealResponse(
        healing_id=result["healing_id"],
        healed_locator=result.get("healed_locator"),
        confidence=result["confidence"],
        confidence_level=result.get("confidence_level", "LOW"),
        decision=result.get("decision", "FAIL"),
        analysis=result["analysis"],
        score_breakdown=result.get("score_breakdown"),
        candidates_evaluated=result.get("candidates_evaluated", 0),
        latency_ms=result["latency_ms"],
    )


def request_headers_tenant(request: Optional[Request] = None) -> str:
    if request:
        return request.headers.get("X-Ghost-Tenant", "default")
    return "default"


def request_headers_project(request: Optional[Request] = None) -> str:
    if request:
        return request.headers.get("X-Ghost-Project", "default")
    return "default"


@app.get("/api/confidence-report")
def confidence_report():
    try:
        return hc.get_confidence_report()
    except Exception as e:
        logger.warning(f"Report data error: {e}")
        return {"message": "No report data yet. Run some tests first."}


@app.post("/api/heal-feedback")
def heal_feedback(request: HealFeedbackRequest, http_req: Request):
    return hc.submit_heal_feedback(
        healing_id=request.healing_id,
        accepted=request.accepted,
        reviewer=request.reviewer,
        notes=request.notes,
        tenant_id=request_headers_tenant(http_req),
        project_id=request_headers_project(http_req),
    )


@app.get("/api/heal-feedback-summary")
def heal_feedback_summary(http_req: Request):
    return hc.get_heal_feedback_summary(
        tenant_id=request_headers_tenant(http_req),
        project_id=request_headers_project(http_req),
    )


@app.get("/api/pending-fixes")
def pending_fixes(
    http_req: Request,
    status: str = "pending_review",
    limit: int = 100,
):
    return hc.get_pending_fixes(
        tenant_id=request_headers_tenant(http_req),
        project_id=request_headers_project(http_req),
        status=status,
        limit=limit,
    )


@app.patch("/api/pending-fixes/{pending_id}")
def pending_fix_update(pending_id: str, body: PendingFixStatusRequest):
    return hc.update_pending_fix(pending_id=pending_id, status=body.status)


@app.get("/api/healing-history")
def healing_history(
    limit: int = 50,
    decision: Optional[str] = None,
    test_name: Optional[str] = None,
):
    return hc.list_recent_heals(limit=limit, decision=decision, test_name=test_name)


@app.get("/api/execution-trace/{healing_id}")
def execution_trace(healing_id: str):
    trace = hc.get_execution_trace(healing_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Healing record '{healing_id}' not found")
    return trace


# ── MCP REST shim (SDK-friendly, no full MCP client required) ─────────────────

MCP_TOOL_MAP = {
    "heal_locator": lambda args: hc.run_heal_locator(
        selector=args["selector"],
        dom_snapshot=args["dom_snapshot"],
        action=args.get("action", "click"),
        page_url=args.get("page_url", ""),
        test_name=args.get("test_name"),
        failure_reason=args.get("failure_reason", "element_not_found"),
        element_hints=args.get("element_hints"),
        tenant_id=args.get("tenant_id", "default"),
        project_id=args.get("project_id", "default"),
    ),
    "health_check": lambda _args: hc.get_health(),
    "get_confidence_report": lambda _args: hc.get_confidence_report(),
    "get_healing_record": lambda args: hc.get_healing_record(args["healing_id"]),
    "list_recent_heals": lambda args: hc.list_recent_heals(
        limit=args.get("limit", 50),
        decision=args.get("decision"),
        test_name=args.get("test_name"),
    ),
    "submit_heal_feedback": lambda args: hc.submit_heal_feedback(
        healing_id=args["healing_id"],
        accepted=args["accepted"],
        tenant_id=args.get("tenant_id", "default"),
        project_id=args.get("project_id", "default"),
        reviewer=args.get("reviewer"),
        notes=args.get("notes"),
    ),
    "get_heal_feedback_summary": lambda args: hc.get_heal_feedback_summary(
        tenant_id=args.get("tenant_id", "default"),
        project_id=args.get("project_id", "default"),
    ),
    "list_pending_fixes": lambda args: hc.get_pending_fixes(
        tenant_id=args.get("tenant_id", "default"),
        project_id=args.get("project_id", "default"),
        status=args.get("status", "pending_review"),
        limit=args.get("limit", 100),
    ),
}


@app.post("/api/mcp/v1/tools/{tool_name}")
async def mcp_tool_call(tool_name: str, body: McpToolCallRequest):
    """Invoke an MCP tool over REST for language SDKs without MCP transport libs."""
    handler = MCP_TOOL_MAP.get(tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Unknown MCP tool: {tool_name}")
    try:
        return handler(body.arguments)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing argument: {exc}") from exc
    except Exception as exc:
        logger.error(f"MCP tool {tool_name} error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/mcp/v1/tools")
def list_mcp_tools():
    return {"tools": list(MCP_TOOL_MAP.keys()), "mcp_http": "/mcp"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
