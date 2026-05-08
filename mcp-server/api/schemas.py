"""
Pydantic schemas for all MCP Server request/response contracts.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HealingDecision(str, Enum):
    AUTO_HEAL = "AUTO_HEAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAIL = "FAIL"


# ── Inbound ──────────────────────────────────────────────────────────────────

class HealRequest(BaseModel):
    original_locator: str = Field(..., description="The failing CSS/XPath/Playwright selector")
    dom_snapshot: str = Field(..., description="Full HTML of the current page")
    failure_reason: str = Field(..., description="Exception message from Playwright")
    page_url: str = Field(..., description="URL of the page where failure occurred")
    action: str = Field(default="click", description="Intended action: click | fill | check")
    test_name: Optional[str] = Field(default=None, description="Test identifier for traceability")
    element_hints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Known element features: {text, tag, type, placeholder, ...}"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "original_locator": "#login-btn",
            "dom_snapshot": "<html>...</html>",
            "failure_reason": "TimeoutError: locator not found within 3000ms",
            "page_url": "http://localhost:3000",
            "action": "click",
            "test_name": "test_login_success",
            "element_hints": {"text": "Login", "tag": "button"}
        }
    }}


# ── Internal ─────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    text_similarity: float
    attribute_similarity: float
    dom_structure_similarity: float
    semantic_role_similarity: float
    visibility_score: float
    final_score: float


class CandidateLocator(BaseModel):
    locator: str
    score: float
    confidence_level: ConfidenceLevel
    score_breakdown: ScoreBreakdown
    element_tag: str
    element_text: str
    element_attributes: Dict[str, str]


# ── Outbound ─────────────────────────────────────────────────────────────────

class HealResponse(BaseModel):
    original_locator: str
    healed_locator: Optional[str]
    confidence_score: float
    confidence_level: ConfidenceLevel
    decision: HealingDecision
    candidates: List[CandidateLocator]
    execution_trace: Dict[str, Any]
    test_name: Optional[str]
    timestamp: datetime
    healing_id: str


class HealingHistoryItem(BaseModel):
    healing_id: str
    test_name: Optional[str]
    original_locator: str
    healed_locator: Optional[str]
    confidence_score: float
    confidence_level: str
    decision: str
    failure_reason: str
    page_url: str
    timestamp: datetime
    was_successful: bool
    score_breakdown: Optional[Dict[str, float]]


class ConfidenceReport(BaseModel):
    total_healed: int
    auto_heal_count: int
    manual_review_count: int
    fail_count: int
    avg_confidence_score: float
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int
    success_rate_percent: float
    score_distribution: List[Dict[str, Any]]
    most_unstable_locators: List[Dict[str, Any]]


class ExecutionTraceResponse(BaseModel):
    healing_id: str
    test_name: Optional[str]
    original_locator: str
    healed_locator: Optional[str]
    decision: str
    confidence_score: float
    score_breakdown: Dict[str, float]
    candidates_evaluated: int
    all_candidates: List[Dict[str, Any]]
    dom_elements_analyzed: int
    timestamp: datetime
    page_url: str
    failure_reason: str
