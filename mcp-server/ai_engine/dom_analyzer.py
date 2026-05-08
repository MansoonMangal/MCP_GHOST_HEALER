"""
DOM Analyzer — parses a full HTML snapshot and extracts all candidate
interactive elements with their feature vectors and DOM paths.
"""
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag

from ai_engine.feature_extractor import (
    extract_features_from_element,
    INTERACTIVE_TAGS,
)
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("dom_analyzer", settings.log_file, settings.log_level)


def _build_dom_path(element: Tag) -> str:
    """Build a simplified CSS-path string for an element (for structure comparison)."""
    parts: List[str] = []
    current = element
    depth = 0
    while current and current.name and depth < 6:
        tag = current.name.lower()
        idx = 1
        for sib in current.previous_siblings:
            if isinstance(sib, Tag) and sib.name == current.name:
                idx += 1
        parts.append(f"{tag}:nth-of-type({idx})")
        current = current.parent
        depth += 1
    return " > ".join(reversed(parts))


def _get_siblings_context(element: Tag, max_siblings: int = 2) -> str:
    """Return text of nearby siblings for context-aware matching."""
    siblings_text: List[str] = []
    count = 0
    for sib in element.previous_siblings:
        if isinstance(sib, Tag) and sib.get_text(strip=True):
            siblings_text.append(sib.get_text(strip=True)[:50])
            count += 1
            if count >= max_siblings:
                break
    for sib in element.next_siblings:
        if isinstance(sib, Tag) and sib.get_text(strip=True):
            siblings_text.append(sib.get_text(strip=True)[:50])
            count += 1
            if count >= max_siblings:
                break
    return " | ".join(siblings_text)


def analyze_dom(
    html_snapshot: str,
    element_hints: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Parse HTML and extract candidate elements for healing.

    Args:
        html_snapshot:  Full page HTML string
        element_hints:  Optional known features to boost relevance filtering

    Returns:
        (candidates_list, total_elements_scanned)
    """
    logger.info("Parsing DOM snapshot for candidate extraction")

    try:
        soup = BeautifulSoup(html_snapshot, "lxml")
    except Exception:
        soup = BeautifulSoup(html_snapshot, "html.parser")

    # Remove script/style noise
    for tag in soup(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()

    all_interactive: List[Tag] = soup.find_all(INTERACTIVE_TAGS)
    total_scanned = len(all_interactive)
    logger.info(f"Found {total_scanned} interactive elements in DOM")

    candidates: List[Dict[str, Any]] = []
    for element in all_interactive:
        dom_path = _build_dom_path(element)
        sibling_ctx = _get_siblings_context(element)
        features = extract_features_from_element(element, dom_path)
        features["sibling_context"] = sibling_ctx

        # Visibility heuristic: hidden inputs / display:none skipped
        style = (element.get("style") or "").lower()
        if "display:none" in style.replace(" ", "") or \
           "visibility:hidden" in style.replace(" ", ""):
            features["is_interactive"] = False

        # Skip purely decorative anchors with no text/id/name
        if (element.name == "a"
                and not features["text"]
                and not features["id"]
                and not features["aria_label"]):
            continue

        candidates.append(features)

    logger.info(f"Extracted {len(candidates)} valid candidates from DOM")
    return candidates, total_scanned
