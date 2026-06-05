"""
Healing Service — central orchestrator for the self-healing pipeline.

Flow:
  HealRequest
    → Feature extraction (from selector string + hints)
    → DOM analysis (parse snapshot, extract candidates)
    → Similarity ranking (weighted score per candidate)
    → Confidence evaluation (AUTO_HEAL / MANUAL_REVIEW / FAIL)
    → Locator validation (uniqueness + interactability check)
    → Persist decision to database
    → Return HealResponse with full trace
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ai_engine.dom_analyzer import analyze_dom
from ai_engine.feature_extractor import extract_features_from_selector
from ai_engine.similarity_engine import rank_candidates
from services.confidence_engine import apply_confidence_rules
from services.locator_validator import validate_locator
from utils.db_manager import (
    get_project_weight_overrides,
    save_healing_record,
    save_failure_log,
    save_confidence_score,
)
from utils.logger import get_logger, log_healing_event, log_score_breakdown
from config.settings import settings

logger = get_logger("healing_service", settings.log_file, settings.log_level)


def _normalize_locator(locator: str) -> str:
    return (locator or "").strip()


def heal(
    original_locator: str,
    dom_snapshot: str,
    failure_reason: str,
    page_url: str,
    action: str = "click",
    test_name: Optional[str] = None,
    element_hints: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full self-healing pipeline. 
    This function is the "brain" of the server. It receives a broken locator
    and a snapshot of the page, and figures out the best new locator.
    """
    healing_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)
    weights = get_project_weight_overrides(
        settings.get_weights(),
        tenant_id=tenant_id,
        project_id=project_id,
    )

    logger.info(
        f"[{healing_id}] Healing started | test={test_name} | locator={original_locator}",
        extra={"healing_id": healing_id, "test_name": test_name},
    )

    # ── Step 1: Extract features from original (failing) selector ─────────
    original_features = extract_features_from_selector(original_locator)
    if element_hints:
        # Merge hints (test-provided ground truth) into extracted features
        for k, v in element_hints.items():
            if v and not original_features.get(k):
                original_features[k] = v
        logger.debug(f"[{healing_id}] Merged element_hints: {element_hints}")

    # ── Step 2: Analyze DOM — extract interactive element candidates ───────
    candidates, total_scanned = analyze_dom(dom_snapshot, element_hints, action=action)

    if not candidates:
        logger.error(f"[{healing_id}] No interactive elements found in DOM")
        result = _build_fail_response(
            healing_id, original_locator, failure_reason,
            page_url, test_name, timestamp, "No interactive elements in DOM", 0
        )
        _persist(result, failure_reason, page_url, test_name)
        return result

    # ── Step 3: Rank candidates via AI Similarity Engine ──────────────────
    # The AI scores each candidate element (0 to 100) based on how similar
    # it is to the original broken element.
    ranked_elements = rank_candidates(original_features, candidates, weights, top_n=5)

    # ── Step 4: Confidence Engine — make a decision ───────────────────────
    # Based on the scores, decide if we can AUTO_HEAL, require MANUAL_REVIEW, or FAIL.
    confidence_result = apply_confidence_rules(ranked_elements)
    best = confidence_result["best_candidate"]
    decision = confidence_result["decision"]
    confidence_level = confidence_result["confidence_level"]

    healed_locator: Optional[str] = None
    confidence_score: float = best["score"] if best else 0.0
    score_breakdown: Dict = best["score_breakdown"] if best else {}

    log_score_breakdown(logger, healing_id, score_breakdown)

    # ── Step 5: Locator validation (for AUTO_HEAL and MANUAL_REVIEW) ──────
    validation_passed = False
    validation_msg = ""
    if best and decision in ("AUTO_HEAL", "MANUAL_REVIEW"):
        validation_passed, validation_msg = validate_locator(
            best["locator"], dom_snapshot, action
        )
        if validation_passed:
            healed_locator = best["locator"]
            if _normalize_locator(healed_locator) == _normalize_locator(original_locator):
                logger.warning(
                    f"[{healing_id}] Healed locator identical to original — rejecting no-op heal."
                )
                healed_locator = None
                decision = "FAIL"
                validation_passed = False
                validation_msg = "Healed locator identical to original selector."
        else:
            # Validation failed — downgrade decision
            logger.warning(f"[{healing_id}] Validation failed: {validation_msg}. Downgrading to FAIL.")
            decision = "FAIL"
            confidence_level = "LOW"

    # ── Step 6: Build full execution trace ───────────────────────────────
    execution_trace = {
        "healing_id": healing_id,
        "steps": [
            {"step": 1, "name": "Feature Extraction", "status": "OK", "detail": f"Extracted from selector: {original_locator}"},
            {"step": 2, "name": "DOM Analysis", "status": "OK", "detail": f"Scanned {total_scanned} elements, {len(candidates)} candidates"},
            {"step": 3, "name": "Similarity Ranking", "status": "OK", "detail": f"Top score: {confidence_score}"},
            {"step": 4, "name": "Confidence Evaluation", "status": "OK", "detail": confidence_result["reasoning"]},
            {"step": 5, "name": "Locator Validation", "status": "OK" if validation_passed else "SKIPPED/FAILED", "detail": validation_msg or "N/A"},
        ],
        "dom_elements_analyzed": total_scanned,
        "candidates_evaluated": len(candidates),
        "all_candidates": [
            {
                "locator": c["locator"],
                "score": c["score"],
                "tag": c["element_tag"],
                "text": c["element_text"],
                "breakdown": c["score_breakdown"],
            }
            for c in ranked_elements
        ],
        "weights_used": weights,
    }

    # ── Step 7: Persist record ────────────────────────────────────────────
    record = {
        "healing_id": healing_id,
        "test_name": test_name,
        "original_locator": original_locator,
        "healed_locator": healed_locator,
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "decision": decision,
        "failure_reason": failure_reason,
        "page_url": page_url,
        "timestamp": timestamp.isoformat(),
        "was_successful": decision == "AUTO_HEAL" and healed_locator is not None,
        "score_breakdown": score_breakdown,
        "dom_elements_analyzed": total_scanned,
        "candidates_evaluated": len(candidates),
        "action": action,
        "tenant_id": tenant_id or "default",
        "project_id": project_id or "default",
        "execution_trace": execution_trace,
    }
    save_healing_record(record)
    save_confidence_score({
        "healing_id": healing_id,
        "score": confidence_score,
        "level": confidence_level,
        "decision": decision,
        "test_name": test_name,
    })
    log_healing_event(logger, record)

    # ── Step 8: Build the final JSON response ─────────────────────────────
    # This dictionary is returned to the Playwright client.
    
    logger.info(f"[{healing_id}] Healing complete | decision={decision} | healed={healed_locator}")

    return {
        "healing_id": healing_id,
        "original_locator": original_locator,
        "healed_locator": healed_locator,
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "decision": decision,
        "candidates": ranked_elements,
        "execution_trace": execution_trace,
        "test_name": test_name,
        "timestamp": timestamp,
        "tenant_id": tenant_id or "default",
        "project_id": project_id or "default",
    }


def get_confidence_level(score: float) -> str:
    if score >= settings.auto_heal_threshold:
        return "HIGH"
    elif score >= settings.manual_review_threshold:
        return "MEDIUM"
    return "LOW"


def _build_fail_response(
    healing_id: str, original_locator: str, failure_reason: str,
    page_url: str, test_name: Optional[str], timestamp: datetime,
    detail: str, total_scanned: int
) -> Dict[str, Any]:
    return {
        "healing_id": healing_id,
        "original_locator": original_locator,
        "healed_locator": None,
        "confidence_score": 0.0,
        "confidence_level": "LOW",
        "decision": "FAIL",
        "candidates": [],
        "execution_trace": {
            "healing_id": healing_id,
            "steps": [{"step": 1, "name": "DOM Analysis", "status": "FAIL", "detail": detail}],
            "dom_elements_analyzed": total_scanned,
            "candidates_evaluated": 0,
            "all_candidates": [],
        },
        "test_name": test_name,
        "timestamp": timestamp,
    }


def _persist(result: Dict, failure_reason: str, page_url: str, test_name: Optional[str]) -> None:
    save_failure_log({
        "healing_id": result["healing_id"],
        "original_locator": result["original_locator"],
        "failure_reason": failure_reason,
        "decision": result["decision"],
        "page_url": page_url,
        "test_name": test_name,
    })
