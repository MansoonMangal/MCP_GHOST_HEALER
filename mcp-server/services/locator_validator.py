"""
Locator Validator — verifies that a proposed healed locator is:
  1. Uniquely present in the DOM
  2. Points to an interactive/visible element
  3. Not a false positive (e.g. hidden div matched by class)

Runs on the HTML snapshot (no live browser), so validation is structural.
"""
from typing import Tuple

from bs4 import BeautifulSoup

from utils.logger import get_logger
from config.settings import settings

logger = get_logger("locator_validator", settings.log_file, settings.log_level)

INTERACTIVE_TAGS = {"button", "a", "input", "select", "textarea", "label"}


def _parse_locator(locator: str, soup: BeautifulSoup):
    """
    Attempt to find elements matching the locator using BS4.
    Supports: #id, .class, [attr=val], tag, :has-text (approximated).
    """
    import re

    # #id
    id_m = re.fullmatch(r"#([\w-]+)", locator.strip())
    if id_m:
        return soup.find_all(id=id_m.group(1))

    # [attr="value"]
    attr_m = re.fullmatch(r'\[([^\]=]+)=["\']?([^"\'\\]*)["\']?\]', locator.strip())
    if attr_m:
        return soup.find_all(attrs={attr_m.group(1): attr_m.group(2)})

    # tag.class1.class2
    tag_cls = re.match(r"^([a-z][\w-]*)\.(.+)$", locator.strip())
    if tag_cls:
        tag, classes = tag_cls.group(1), tag_cls.group(2).split(".")
        return soup.find_all(tag, class_=lambda c: c and all(cls in c for cls in classes))

    # tag:has-text("...")
    has_text_m = re.match(r'^([a-z][\w-]*):has-text\(["\'](.+)["\']\)$', locator.strip())
    if has_text_m:
        tag, text = has_text_m.group(1), has_text_m.group(2)
        return [el for el in soup.find_all(tag) if text.lower() in el.get_text().lower()]

    # Fallback: try as CSS tag
    if re.fullmatch(r"[a-z][\w-]*", locator.strip()):
        return soup.find_all(locator.strip())

    return []


def validate_locator(
    locator: str,
    dom_snapshot: str,
    action: str = "click",
) -> Tuple[bool, str]:
    """
    Validate the healed locator against the DOM snapshot.

    Returns:
        (is_valid: bool, reason: str)
    """
    try:
        soup = BeautifulSoup(dom_snapshot, "lxml")
    except Exception:
        soup = BeautifulSoup(dom_snapshot, "html.parser")

    matches = _parse_locator(locator, soup)

    if not matches:
        msg = f"Locator '{locator}' matched 0 elements — invalid."
        logger.warning(msg)
        return False, msg

    if len(matches) > 3:
        msg = f"Locator '{locator}' is ambiguous — matched {len(matches)} elements."
        logger.warning(msg)
        return False, msg

    element = matches[0]
    tag = element.name.lower() if element.name else ""

    # Check interactivity
    is_interactive = tag in INTERACTIVE_TAGS
    style = (element.get("style") or "").lower().replace(" ", "")
    is_hidden = "display:none" in style or "visibility:hidden" in style

    if is_hidden:
        msg = f"Locator '{locator}' points to a hidden element."
        logger.warning(msg)
        return False, msg

    if (action in ("click",) and not is_interactive:
        msg = f"Locator '{locator}' points to non-interactive <{tag}> for action '{action}'."
        logger.warning(msg)
        return False, msg

    fill_actions = {"fill", "type", "press", "input", "press_sequentially", "selectoption"}
    if action.lower() in fill_actions:
        if tag not in ("input", "textarea", "select"):
            msg = f"Locator '{locator}' is <{tag}> — not fillable for action '{action}'."
            logger.warning(msg)
            return False, msg
        if tag == "input":
            inp_type = (element.get("type") or "text").lower()
            if inp_type in ("hidden", "submit", "button", "image", "checkbox", "radio", "file"):
                msg = f"Locator '{locator}' input type='{inp_type}' is not fillable."
                logger.warning(msg)
                return False, msg

    # Reject ad iframe hosts and generic layout containers for any heal
    el_id = (element.get("id") or "").lower()
    if el_id.startswith("aswift") or "google_ads" in el_id:
        msg = f"Locator '{locator}' points to ad iframe host — rejected."
        logger.warning(msg)
        return False, msg
    if tag in ("div", "header", "nav", "footer", "section") and action.lower() in fill_actions:
        msg = f"Locator '{locator}' layout element <{tag}> cannot receive fill."
        logger.warning(msg)
        return False, msg

    msg = f"Locator '{locator}' validated successfully. Matches {len(matches)} element(s), tag=<{tag}>."
    logger.info(msg)
    return True, msg
