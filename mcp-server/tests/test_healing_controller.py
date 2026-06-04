"""Unit tests for unified healing controller."""
import pytest

from controllers.healing_controller import (
    get_health,
    run_heal_locator,
    _normalize_confidence,
)


def test_normalize_confidence_from_percent():
    assert _normalize_confidence(85.0) == 0.85


def test_normalize_confidence_already_decimal():
    assert _normalize_confidence(0.75) == 0.75


def test_get_health_includes_mcp():
    data = get_health()
    assert data["status"] == "healthy"
    assert data["protocol"] == "mcp-v1"
    assert "mcp_endpoint" in data


SAMPLE_DOM = """
<html><body>
<button id="submit-btn">Submit</button>
<button id="login-btn">Login</button>
</body></html>
"""


def test_run_heal_locator_returns_structure():
    result = run_heal_locator(
        selector="#submit-btn",
        dom_snapshot=SAMPLE_DOM,
        action="click",
    )
    assert "healing_id" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
    assert result["decision"] in ("AUTO_HEAL", "MANUAL_REVIEW", "FAIL")
