"""Contract tests for REST and MCP shim parity."""
import pytest
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

SAMPLE_DOM = '<html><body><button id="ok">OK</button></body></html>'


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["protocol"] == "mcp-v1"


def test_readiness_endpoint():
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True


def test_readiness_public_when_api_key_required(monkeypatch):
    """Render health checks must work without X-API-Key when GHOST_API_KEY is set."""
    from config.settings import settings

    monkeypatch.setenv("GHOST_API_KEY", "test-secret-key")
    monkeypatch.setattr(settings, "api_key", "test-secret-key")
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True


def test_list_mcp_tools():
    r = client.get("/api/mcp/v1/tools")
    assert r.status_code == 200
    tools = r.json()["tools"]
    assert "heal_locator" in tools
    assert "health_check" in tools


def test_mcp_shim_heal_locator():
    r = client.post(
        "/api/mcp/v1/tools/heal_locator",
        json={
            "arguments": {
                "selector": "#ok",
                "dom_snapshot": SAMPLE_DOM,
                "action": "click",
            }
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "healing_id" in data
    assert "confidence" in data


def test_rest_heal_locator_parity_fields():
    r = client.post(
        "/api/heal-locator",
        json={"selector": "#ok", "dom_snapshot": SAMPLE_DOM, "action": "click"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "healing_id" in data
    assert "confidence" in data
    assert "decision" in data


def test_feedback_endpoints_roundtrip():
    heal = client.post(
        "/api/heal-locator",
        json={"selector": "#ok", "dom_snapshot": SAMPLE_DOM, "action": "click"},
    )
    assert heal.status_code == 200
    healing_id = heal.json()["healing_id"]

    fb = client.post(
        "/api/heal-feedback",
        json={"healing_id": healing_id, "accepted": True, "reviewer": "ci"},
    )
    assert fb.status_code == 200
    assert fb.json()["ok"] is True

    summary = client.get("/api/heal-feedback-summary")
    assert summary.status_code == 200
    assert "total_feedback" in summary.json()
