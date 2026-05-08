"""
Confidence Engine — applies threshold rules and assigns decision labels.

Scoring rules:
  score >= 85  → HIGH  → AUTO_HEAL
  score 60–84  → MEDIUM → MANUAL_REVIEW
  score < 60   → LOW   → FAIL
"""
from typing import Any, Dict, List, Optional

from config.settings import settings
from utils.logger import get_logger

logger = get_logger("confidence_engine", settings.log_file, settings.log_level)


def get_confidence_level(score: float) -> str:
    if score >= settings.auto_heal_threshold:
        return "HIGH"
    elif score >= settings.manual_review_threshold:
        return "MEDIUM"
    return "LOW"


def get_decision(score: float) -> str:
    if score >= settings.auto_heal_threshold:
        return "AUTO_HEAL"
    elif score >= settings.manual_review_threshold:
        return "MANUAL_REVIEW"
    return "FAIL"


def apply_confidence_rules(ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate ranked candidates and return a structured decision.

    Returns:
        {
          decision:         AUTO_HEAL | MANUAL_REVIEW | FAIL,
          confidence_level: HIGH | MEDIUM | LOW,
          best_candidate:   dict | None,
          all_candidates:   list,
          reasoning:        str
        }
    """
    if not ranked_candidates:
        logger.warning("No candidates to evaluate — decision: FAIL")
        return {
            "decision": "FAIL",
            "confidence_level": "LOW",
            "best_candidate": None,
            "all_candidates": [],
            "reasoning": "No candidate elements found in DOM snapshot.",
        }

    best = ranked_candidates[0]
    score = best["score"]
    decision = get_decision(score)
    confidence_level = get_confidence_level(score)

    reasoning_map = {
        "AUTO_HEAL": (
            f"Score {score:.1f} ≥ {settings.auto_heal_threshold} threshold. "
            "High-confidence match found — automatic healing approved."
        ),
        "MANUAL_REVIEW": (
            f"Score {score:.1f} is between {settings.manual_review_threshold} and "
            f"{settings.auto_heal_threshold}. Healing attempted with caution. "
            "Human review recommended."
        ),
        "FAIL": (
            f"Score {score:.1f} < {settings.manual_review_threshold} threshold. "
            "No confident match found. Manual intervention required."
        ),
    }

    logger.info(
        f"Confidence decision | score={score:.1f} | level={confidence_level} | decision={decision}",
        extra={"healing_decision": decision, "confidence_score": score},
    )

    return {
        "decision": decision,
        "confidence_level": confidence_level,
        "best_candidate": best,
        "all_candidates": ranked_candidates,
        "reasoning": reasoning_map[decision],
    }
