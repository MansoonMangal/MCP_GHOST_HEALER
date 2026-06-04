"""Confidence engine unit tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp-server"))

from services.confidence_engine import apply_confidence_rules, get_decision


def test_fail_when_no_candidates():
    result = apply_confidence_rules([])
    assert result["decision"] == "FAIL"


def test_auto_heal_high_score():
    candidates = [{"score": 90.0, "locator": "#btn", "score_breakdown": {}}]
    result = apply_confidence_rules(candidates)
    assert result["decision"] == "AUTO_HEAL"
    assert get_decision(90.0) == "AUTO_HEAL"
