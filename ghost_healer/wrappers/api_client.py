"""
API Client — handles communication with the MCP Healing Server.
"""
import logging
from typing import Any, Dict, Optional
import httpx
from ghost_framework.wrappers.models import HealResult

logger = logging.getLogger("api_client")

class MCPClient:
    """
    Client for the AI Healing Server.
    """
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url.rstrip("/")

    def request_healing(
        self,
        selector: str,
        dom_snapshot: str,
        failure_reason: str,
        page_url: str,
        action: str,
        hints: Optional[Dict[str, Any]],
        test_name: Optional[str],
        screenshot_b64: Optional[str] = None,
    ) -> HealResult:
        """
        Sends context to AI server and returns a simplified HealResult.
        """
        payload = {
            "original_locator": selector,
            "dom_snapshot": dom_snapshot,
            "failure_reason": failure_reason,
            "page_url": page_url,
            "action": action,
            "test_name": test_name,
            "element_hints": hints,
        }
        
        try:
            response = httpx.post(
                f"{self.mcp_server_url}/api/heal-locator",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            return HealResult(
                healed_locator=data.get("healed_locator"),
                confidence_score=data.get("confidence_score", 0.0),
                analysis_time_ms=data.get("analysis_time_ms", 0.0),
                found_via="ai",
                failure_reason=None
            )
            
        except Exception as e:
            logger.error(f"MCP server request failed: {e}")
            return HealResult(
                healed_locator=None,
                confidence_score=0.0,
                analysis_time_ms=0.0,
                found_via="none",
                failure_reason=str(e)
            )

# Singleton instance
from ghost_framework.config.framework_config import config
api_client = MCPClient(config.mcp_server_url)
