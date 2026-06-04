"""Unified healing API controller — single source of truth for REST and MCP."""
import time
from typing import Any, Dict, List, Optional

from config.settings import settings
from services.healing_service import heal
from utils.db_manager import (
    get_all_healing_records,
    get_confidence_report_data,
    get_feedback_summary,
    get_healing_record_by_id,
    list_pending_fixes,
    save_heal_feedback,
    save_pending_fix,
    update_pending_fix_status,
)


def _normalize_confidence(score: float) -> float:
    """Return confidence in 0-1 range."""
    if score > 1.0:
        return round(score / 100.0, 4)
    return round(score, 4)


def run_heal_locator(
    selector: str,
    dom_snapshot: str,
    action: str = "click",
    page_url: str = "",
    test_name: Optional[str] = None,
    failure_reason: str = "element_not_found",
    element_hints: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default",
    project_id: str = "default",
) -> Dict[str, Any]:
    """Execute healing pipeline and return normalized response dict."""
    start = time.time()
    result = heal(
        original_locator=selector,
        dom_snapshot=dom_snapshot,
        failure_reason=failure_reason,
        page_url=page_url or "",
        action=action,
        test_name=test_name,
        element_hints=element_hints,
        tenant_id=tenant_id,
        project_id=project_id,
    )
    latency = (time.time() - start) * 1000

    steps = result.get("execution_trace", {}).get("steps", [])
    analysis = steps[-1]["detail"] if steps else result.get("decision", "No analysis available")

    best_candidates = result.get("candidates", [])
    breakdown = best_candidates[0].get("score_breakdown", {}) if best_candidates else {}

    raw_score = result.get("confidence_score", 0.0)

    locator_quality_score = 0.0
    if breakdown:
        locator_quality_score = round(
            (
                breakdown.get("attribute_similarity", 0.0) * 0.4
                + breakdown.get("semantic_role_similarity", 0.0) * 0.3
                + breakdown.get("dom_structure_similarity", 0.0) * 0.2
                + breakdown.get("visibility_score", 0.0) * 0.1
            )
            / 100.0,
            4,
        )

    response = {
        "healing_id": result["healing_id"],
        "healed_locator": result.get("healed_locator"),
        "confidence": _normalize_confidence(raw_score),
        "confidence_score_raw": raw_score,
        "confidence_level": result.get("confidence_level", "LOW"),
        "decision": result.get("decision", "FAIL"),
        "analysis": analysis,
        "score_breakdown": breakdown,
        "candidates_evaluated": result.get("candidates_evaluated", 0),
        "latency_ms": round(latency, 2),
        "execution_trace": result.get("execution_trace"),
        "locator_quality_score": locator_quality_score,
        "tenant_id": tenant_id,
        "project_id": project_id,
    }
    if response["decision"] == "MANUAL_REVIEW" and response.get("healed_locator"):
        save_pending_fix(
            {
                "healing_id": response["healing_id"],
                "tenant_id": tenant_id,
                "project_id": project_id,
                "old_locator": selector,
                "suggested_locator": response["healed_locator"],
                "confidence": response["confidence"],
                "reason": "manual_review_threshold",
                "status": "pending_review",
            }
        )
    return response


def get_health() -> Dict[str, Any]:
    from utils.db_manager import STORAGE_BACKEND

    return {
        "status": "healthy",
        "version": "4.0.0",
        "engine": "real-dna-matcher",
        "protocol": "mcp-v1",
        "storage_backend": STORAGE_BACKEND,
        "auto_heal_threshold": settings.auto_heal_threshold,
        "mcp_endpoint": "/mcp",
    }


def get_confidence_report() -> Dict[str, Any]:
    return get_confidence_report_data()


def submit_heal_feedback(
    *,
    healing_id: str,
    accepted: bool,
    tenant_id: str = "default",
    project_id: str = "default",
    reviewer: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    save_heal_feedback(
        {
            "healing_id": healing_id,
            "accepted": accepted,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "reviewer": reviewer,
            "notes": notes,
        }
    )
    return {"ok": True, "healing_id": healing_id, "accepted": accepted}


def get_heal_feedback_summary(
    tenant_id: str = "default",
    project_id: str = "default",
) -> Dict[str, Any]:
    return get_feedback_summary(tenant_id=tenant_id, project_id=project_id)


def get_pending_fixes(
    tenant_id: str = "default",
    project_id: str = "default",
    status: str = "pending_review",
    limit: int = 100,
) -> List[Dict[str, Any]]:
    return list_pending_fixes(
        tenant_id=tenant_id,
        project_id=project_id,
        status=status,
        limit=limit,
    )


def update_pending_fix(pending_id: str, status: str) -> Dict[str, Any]:
    ok = update_pending_fix_status(pending_id=pending_id, status=status)
    return {"ok": ok, "pending_id": pending_id, "status": status}


def get_healing_record(healing_id: str) -> Optional[Dict[str, Any]]:
    return get_healing_record_by_id(healing_id)


def list_recent_heals(
    limit: int = 50,
    decision: Optional[str] = None,
    test_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    records = get_all_healing_records()
    if decision:
        records = [r for r in records if r.get("decision") == decision.upper()]
    if test_name:
        records = [r for r in records if r.get("test_name") == test_name]
    return records[:limit]


def get_execution_trace(healing_id: str) -> Optional[Dict[str, Any]]:
    record = get_healing_record_by_id(healing_id)
    if not record:
        return None
    trace = record.get("execution_trace") or {}
    return {
        "healing_id": healing_id,
        "test_name": record.get("test_name"),
        "original_locator": record.get("original_locator", ""),
        "healed_locator": record.get("healed_locator"),
        "decision": record.get("decision", "FAIL"),
        "confidence_score": record.get("confidence_score", 0.0),
        "score_breakdown": record.get("score_breakdown", {}),
        "candidates_evaluated": record.get("candidates_evaluated", 0),
        "all_candidates": trace.get("all_candidates", []),
        "dom_elements_analyzed": record.get("dom_elements_analyzed", 0),
        "timestamp": record.get("timestamp", ""),
        "page_url": record.get("page_url", ""),
        "failure_reason": record.get("failure_reason", ""),
    }
