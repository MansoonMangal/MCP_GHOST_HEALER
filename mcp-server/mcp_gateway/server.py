"""
MCP gateway — exposes Ghost Healer Brain as Model Context Protocol tools/resources.
"""
import json
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from controllers.healing_controller import (
    get_confidence_report,
    get_heal_feedback_summary,
    get_health,
    get_healing_record,
    get_pending_fixes,
    list_recent_heals,
    run_heal_locator,
    submit_heal_feedback,
)

mcp = FastMCP(
    "Ghost Healer Brain",
    instructions=(
        "AI self-healing brain for Playwright and Selenium automation. "
        "Use heal_locator when a locator fails; query reports for analytics."
    ),
)


@mcp.tool()
def heal_locator(
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
    """Heal a broken locator using DOM snapshot and similarity scoring."""
    return run_heal_locator(
        selector=selector,
        dom_snapshot=dom_snapshot,
        action=action,
        page_url=page_url,
        test_name=test_name,
        failure_reason=failure_reason,
        element_hints=element_hints,
        tenant_id=tenant_id,
        project_id=project_id,
    )


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Return brain health, version, and protocol metadata."""
    return get_health()


@mcp.tool()
def get_confidence_report_tool() -> Dict[str, Any]:
    """Aggregated healing analytics and score distribution."""
    return get_confidence_report()


@mcp.tool()
def get_healing_record_tool(healing_id: str) -> Dict[str, Any]:
    """Fetch a single healing record by ID."""
    record = get_healing_record(healing_id)
    if not record:
        return {"error": f"Healing record '{healing_id}' not found"}
    return record


@mcp.tool()
def list_recent_heals_tool(
    limit: int = 50,
    decision: Optional[str] = None,
    test_name: Optional[str] = None,
) -> list:
    """List recent healing decisions, newest first."""
    return list_recent_heals(limit=limit, decision=decision, test_name=test_name)


@mcp.tool()
def submit_heal_feedback_tool(
    healing_id: str,
    accepted: bool,
    tenant_id: str = "default",
    project_id: str = "default",
    reviewer: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Store user decision for adaptive scoring."""
    return submit_heal_feedback(
        healing_id=healing_id,
        accepted=accepted,
        tenant_id=tenant_id,
        project_id=project_id,
        reviewer=reviewer,
        notes=notes,
    )


@mcp.tool()
def get_heal_feedback_summary_tool(
    tenant_id: str = "default",
    project_id: str = "default",
) -> Dict[str, Any]:
    """Return acceptance/rejection summary for a project."""
    return get_heal_feedback_summary(tenant_id=tenant_id, project_id=project_id)


@mcp.tool()
def list_pending_fixes_tool(
    tenant_id: str = "default",
    project_id: str = "default",
    status: str = "pending_review",
    limit: int = 100,
) -> list:
    """List pending fixes for human approval workflow."""
    return get_pending_fixes(
        tenant_id=tenant_id,
        project_id=project_id,
        status=status,
        limit=limit,
    )


@mcp.resource("ghost://engine/metadata")
def engine_metadata() -> str:
    """Engine version and threshold configuration."""
    meta = get_health()
    return json.dumps(meta, indent=2)


@mcp.resource("ghost://analytics/confidence-trends")
def confidence_trends() -> str:
    """Aggregated confidence report as JSON."""
    return json.dumps(get_confidence_report(), indent=2, default=str)


@mcp.resource("ghost://heals/recent")
def recent_heals_resource() -> str:
    """Ten most recent healing records."""
    return json.dumps(list_recent_heals(limit=10), indent=2, default=str)


def create_mcp_asgi_app():
    """Streamable HTTP transport for Render / remote MCP clients."""
    return mcp.streamable_http_app()
