"""
MCP-first brain client — calls /api/mcp/v1/tools/{tool} with REST fallback.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from ghost_healer.core.config import settings

logger = logging.getLogger("GhostMCPClient")


class BrainClient:
    """Unified client: MCP REST shim first, legacy REST fallback."""

    def __init__(self):
        self.base_url = settings.mcp_server.url.rstrip("/")
        self.timeout = settings.mcp_server.timeout
        self.api_key = settings.mcp_server.api_key
        self.protocol = getattr(settings.mcp_server, "protocol", "mcp-first")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "X-Ghost-Protocol": "mcp-v1"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        headers["X-Ghost-Tenant"] = settings.mcp_server.tenant_id
        headers["X-Ghost-Project"] = settings.mcp_server.project_id
        return headers

    def heal_locator(
        self,
        selector: str,
        action: str,
        dom_snapshot: str,
        page_url: Optional[str] = None,
        framework: Optional[str] = None,
        test_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "selector": selector,
            "action": action,
            "dom_snapshot": dom_snapshot,
            "page_url": page_url or "",
            "test_name": test_name,
            "failure_reason": "element_not_found",
            "tenant_id": settings.mcp_server.tenant_id,
            "project_id": settings.mcp_server.project_id,
        }
        if framework:
            payload["framework"] = framework

        with httpx.Client(timeout=self.timeout) as client:
            if self.protocol in ("mcp-first", "mcp"):
                try:
                    resp = client.post(
                        f"{self.base_url}/api/mcp/v1/tools/heal_locator",
                        json={"arguments": payload},
                        headers=self._headers(),
                    )
                    if resp.status_code == 200:
                        return resp.json()
                except Exception as exc:
                    logger.debug(f"MCP shim failed, falling back to REST: {exc}")

            resp = client.post(
                f"{self.base_url}/api/heal-locator",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    def health_check(self) -> Dict[str, Any]:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{self.base_url}/health", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def submit_feedback(
        self,
        healing_id: str,
        accepted: bool,
        reviewer: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "healing_id": healing_id,
            "accepted": accepted,
            "reviewer": reviewer,
            "notes": notes,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/heal-feedback",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()


brain_client = BrainClient()
