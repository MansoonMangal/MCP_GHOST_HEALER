"""
Similarity Engine — weighted multi-feature scoring model.

Formula:
  final_score = (text_sim × 0.35)
              + (attr_sim  × 0.25)
              + (dom_struct × 0.20)
              + (semantic   × 0.10)
              + (visibility × 0.10)

Uses rapidfuzz for high-performance fuzzy string matching.
"""
from typing import Any, Dict, List, Tuple

from rapidfuzz import fuzz

from ai_engine.feature_extractor import build_locator_from_element
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("similarity_engine", settings.log_file, settings.log_level)


# ── Individual similarity functions ───────────────────────────────────────────

def _text_similarity(orig: Dict, cand: Dict) -> float:
    """Compare visible text content using token sort ratio (handles word order)."""
    orig_text = (orig.get("text") or "").strip().lower()
    cand_text = (cand.get("text") or "").strip().lower()
    if not orig_text:
        return 100.0  # Original didn't specify text constraint -> neutral/perfect score
    if not cand_text:
        return 10.0   # Original required text, candidate has none -> penalize
    return fuzz.token_sort_ratio(orig_text, cand_text)


def _attribute_similarity(orig: Dict, cand: Dict) -> float:
    """
    Compare element attributes using a weighted sub-score.
    High-signal attributes (like `id` or `data-testid`) are worth more points than generic ones (like `class`).
    """
    comparisons: List[Tuple[str, float]] = [
        ("id", 2.0),
        ("name", 1.5),
        ("data_testid", 2.0),
        ("data_qa", 2.0),
        ("aria_label", 1.5),
        ("type", 1.0),
        ("placeholder", 1.0),
        ("class_str", 0.8),
    ]
    weighted_sum = 0.0
    total_weight = 0.0

    for attr, weight in comparisons:
        orig_val = str(orig.get(attr) or "").strip().lower()
        cand_val = str(cand.get(attr) or "").strip().lower()
        # If the original selector required an attribute, we check how closely it matches the candidate's.
        if orig_val and cand_val:
            if orig_val == cand_val:
                score = 100.0
            elif orig_val in cand_val or cand_val in orig_val:
                score = 85.0 + (fuzz.ratio(orig_val, cand_val) * 0.15)  # Boost score for substring matches
            else:
                score = fuzz.ratio(orig_val, cand_val)
        elif not orig_val and cand_val:
            score = 100.0  # Original didn't specify, candidate has it -> ignore/don't penalize
        elif not orig_val and not cand_val:
            score = 100.0  # Both missing -> matches constraint
        else:
            score = 0.0    # Original required it, candidate missing it -> penalize

        weighted_sum += score * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 50.0


def _dom_structure_similarity(orig: Dict, cand: Dict) -> float:
    """Compare tag names and DOM path depth."""
    orig_tag = (orig.get("tag_name") or "").lower()
    cand_tag = (cand.get("tag_name") or "").lower()
    if not orig_tag:
        tag_score = 100.0  # Not specified in original selector -> ignore
    else:
        if orig_tag == cand_tag:
            tag_score = 100.0
        elif (orig_tag == "button" and cand_tag == "input" and cand.get("type") in ("submit", "button")):
            tag_score = 90.0
        elif (orig_tag == "input" and cand_tag == "button" and cand.get("role") == "button"):
            tag_score = 90.0
        else:
            tag_score = 20.0

    orig_path = orig.get("dom_path") or orig.get("tag_name") or ""
    cand_path = cand.get("dom_path") or cand.get("tag_name") or ""
    path_score = fuzz.ratio(orig_path, cand_path) if orig_path and cand_path else 50.0

    return (tag_score * 0.55) + (path_score * 0.45)


def _semantic_role_similarity(orig: Dict, cand: Dict) -> float:
    """Compare semantic roles (explicit role attr or inferred from tag)."""
    if not orig.get("role") and not orig.get("tag_name"):
        return 100.0  # Not specified in original selector -> ignore

    def effective_role(f: Dict) -> str:
        if f.get("role"):
            return f["role"].lower()
        tag = f.get("tag_name", "")
        if tag == "input":
            t = f.get("type", "").lower()
            if t in ("button", "submit", "image", "reset"):
                return "button"
            elif t in ("checkbox", "radio"):
                return t
        role_map = {
            "button": "button", "a": "link", "input": "textbox",
            "select": "listbox", "textarea": "textbox", "label": "label",
        }
        return role_map.get(tag, tag)

    orig_role = effective_role(orig)
    cand_role = effective_role(cand)
    return 100.0 if orig_role == cand_role else fuzz.ratio(orig_role, cand_role)


def _visibility_score(cand: Dict) -> float:
    """Score based on whether the element is interactive and visible."""
    if cand.get("is_interactive"):
        return 100.0
    return 40.0


# ── Main scoring function ─────────────────────────────────────────────────────

def compute_score(
    original_features: Dict[str, Any],
    candidate_features: Dict[str, Any],
    weights: Dict[str, float],
) -> Tuple[float, Dict[str, float]]:
    """
    Compute the weighted final score for a single candidate element.

    Returns:
        (final_score_0_to_100, score_breakdown_dict)
    """
    text_sim = _text_similarity(original_features, candidate_features)
    attr_sim = _attribute_similarity(original_features, candidate_features)
    dom_sim = _dom_structure_similarity(original_features, candidate_features)
    semantic_sim = _semantic_role_similarity(original_features, candidate_features)
    visibility = _visibility_score(candidate_features)

    final = (
        text_sim   * weights["text_similarity"]
        + attr_sim * weights["attribute_similarity"]
        + dom_sim  * weights["dom_structure"]
        + semantic_sim * weights["semantic_role"]
        + visibility   * weights["visibility"]
    )

    # ── Strong Penalty: Action Mismatch ──────────────────────────────────
    # If the element type doesn't match the action (e.g. clicking an input),
    # we apply a massive penalty to ensure it's not picked over a valid type.
    if candidate_features.get("action_mismatch"):
        final -= 50.0


    breakdown = {
        "text_similarity": round(text_sim, 2),
        "attribute_similarity": round(attr_sim, 2),
        "dom_structure_similarity": round(dom_sim, 2),
        "semantic_role_similarity": round(semantic_sim, 2),
        "visibility_score": round(visibility, 2),
        "final_score": round(final, 2),
    }

    return round(final, 2), breakdown


def rank_candidates(
    original_features: Dict[str, Any],
    all_candidates: List[Dict[str, Any]],
    weights: Dict[str, float],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Score all DOM candidates and return top_n ranked results.

    Each result contains:
      locator, score, score_breakdown, element metadata
    """
    logger.info(f"Ranking {len(all_candidates)} candidates against original features")
    scored: List[Dict[str, Any]] = []

    for candidate in all_candidates:
        score, breakdown = compute_score(original_features, candidate, weights)
        locator = build_locator_from_element(candidate)

        scored.append({
            "locator": locator,
            "score": score,
            "score_breakdown": breakdown,
            "element_tag": candidate.get("tag_name", ""),
            "element_text": candidate.get("text", "")[:100],
            "element_attributes": {
                k: candidate.get(k, "")
                for k in ["id", "class_str", "name", "type", "aria_label", "data_testid", "data_qa"]
            },
            "_features": candidate,
        })

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    top = ranked[:top_n]
    logger.info(f"Top candidate: score={top[0]['score'] if top else 'N/A'}, locator={top[0]['locator'] if top else 'N/A'}")
    return top
