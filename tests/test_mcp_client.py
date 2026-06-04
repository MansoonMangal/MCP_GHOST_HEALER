"""Python SDK MCP client tests (mocked)."""
from unittest.mock import patch, MagicMock

from ghost_healer.core.mcp_client import BrainClient


def test_brain_client_mcp_first_fallback():
    client = BrainClient()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "healed_locator": "#new",
        "confidence": 0.9,
        "decision": "AUTO_HEAL",
    }

    with patch("httpx.Client") as mock_client_cls:
        instance = mock_client_cls.return_value.__enter__.return_value
        instance.post.return_value = mock_resp

        result = client.heal_locator(
            selector="#old",
            action="click",
            dom_snapshot="<html></html>",
        )
        assert result["healed_locator"] == "#new"
        assert instance.post.call_count >= 1
