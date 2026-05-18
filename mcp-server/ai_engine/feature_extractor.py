"""
Feature Extractor — pulls structured feature vectors from DOM elements
and from the original failing selector string.
"""
import re
from typing import Any, Dict
from bs4 import Tag


# Interactive HTML tags we care about for locator healing
INTERACTIVE_TAGS = {
    "button", "a", "input", "select", "textarea", "label", "summary", "details",
    "h1", "h2", "h3", "h4", "h5", "h6", "span", "div", "p", "i", "img"
}


# ── From selector string ──────────────────────────────────────────────────────

def extract_features_from_selector(selector: str) -> Dict[str, Any]:
    """
    Reverse-engineer a broken selector string (like '#login-btn' or '//button') 
    back into its core features (tag=button, id=login-btn).
    
    Why? Because the original element is missing from the page! 
    We use Regular Expressions (Regex) to guess what the element *used to* look like
    so the AI knows what to search for.
    """
    # Normalize and strip escaping backslashes from selector
    selector = selector.replace('\\"', '"').replace("\\'", "'").replace('\\', '')

    features: Dict[str, Any] = {
        "tag_name": "",
        "text": "",
        "id": "",
        "class_list": [],
        "name": "",
        "type": "",
        "placeholder": "",
        "aria_label": "",
        "role": "",
        "data_testid": "",
        "data_qa": "",
        "dom_path": selector,
        "is_interactive": False,
    }

    # Playwright text= selector
    if selector.startswith("text="):
        features["text"] = selector[5:].strip("'\"")
        return features

    # Playwright role= selector  e.g. role=button[name="Login"]
    if selector.startswith("role="):
        role_match = re.match(r"role=(\w+)(?:\[name=['\"]?([^'\"\\]]*)['\"]?\])?", selector)
        if role_match:
            features["role"] = role_match.group(1)
            if role_match.group(2):
                features["text"] = role_match.group(2)
        return features

    # XPath
    if selector.startswith("//") or selector.startswith("xpath="):
        sel = selector.replace("xpath=", "")
        text_m = re.search(r"(?:text\(\)|\.)\s*=\s*['\"]([^'\"]+)['\"]", sel)
        if text_m:
            features["text"] = text_m.group(1)
        contains_m = re.search(r"contains\([^,]+,\s*['\"]([^'\"]+)['\"]", sel)
        if contains_m:
            features["text"] = contains_m.group(1)
        tag_m = re.search(r"//(\w+)", sel)
        if tag_m:
            features["tag_name"] = tag_m.group(1)
            features["is_interactive"] = features["tag_name"] in INTERACTIVE_TAGS
        return features

    # CSS selector
    id_m = re.search(r"#([\w-]+)", selector)
    if id_m:
        features["id"] = id_m.group(1)

    class_m = re.findall(r"\.([\w-]+)", selector)
    if class_m:
        features["class_list"] = class_m

    tag_m = re.match(r"^([a-zA-Z][\w-]*)", selector)
    if tag_m:
        features["tag_name"] = tag_m.group(1).lower()

    # Attribute extraction  [attr="value"]
    attr_m = re.findall(r"\[([^\]=]+)(?:=|~=|\|=)['\"]?([^'\"\]]*)['\"]?\]", selector)
    for attr_name, attr_value in attr_m:
        attr_name = attr_name.strip().lower().replace("-", "_")
        if attr_name == "id":
            features["id"] = attr_value
        elif attr_name == "class":
            features["class_list"] = attr_value.split()
        elif attr_name == "name":
            features["name"] = attr_value
        elif attr_name == "type":
            features["type"] = attr_value
        elif attr_name == "placeholder":
            features["placeholder"] = attr_value
        elif attr_name in ("aria_label", "aria-label"):
            features["aria_label"] = attr_value
        elif attr_name in ("data_testid", "data-testid"):
            features["data_testid"] = attr_value
        elif attr_name in ("data_qa", "data-qa"):
            features["data_qa"] = attr_value
        elif attr_name == "role":
            features["role"] = attr_value

    features["is_interactive"] = features["tag_name"] in INTERACTIVE_TAGS
    
    # Smart Inference: If tag is missing, guess from ID/Path keywords
    if not features["tag_name"]:
        path_lower = features["dom_path"].lower()
        if any(k in path_lower for k in ["btn", "submit", "button"]):
            features["tag_name"] = "button"
            features["role"] = "button"
            features["is_interactive"] = True
        elif any(k in path_lower for k in ["email", "pass", "input", "text"]):
            features["tag_name"] = "input"
            features["role"] = "textbox"
            features["is_interactive"] = True
            
    return features


# ── From live DOM element (BeautifulSoup Tag) ─────────────────────────────────

def extract_features_from_element(element: Tag, dom_path: str = "") -> Dict[str, Any]:
    """Extract a normalized feature vector from a BeautifulSoup Tag."""
    tag_name = element.name.lower() if element.name else ""
    attrs = element.attrs or {}

    # class can be a list in BS4
    raw_class = attrs.get("class", [])
    class_list = raw_class if isinstance(raw_class, list) else raw_class.split()

    # Text content — direct text only (not nested), stripped
    direct_text = element.get_text(separator=" ", strip=True)[:200]

    return {
        "tag_name": tag_name,
        "text": direct_text,
        "id": attrs.get("id", ""),
        "class_list": class_list,
        "class_str": " ".join(class_list),
        "name": attrs.get("name", ""),
        "type": attrs.get("type", ""),
        "placeholder": attrs.get("placeholder", ""),
        "aria_label": attrs.get("aria-label", ""),
        "role": attrs.get("role", ""),
        "data_testid": attrs.get("data-testid", ""),
        "data_qa": attrs.get("data-qa", ""),
        "href": attrs.get("href", ""),
        "value": attrs.get("value", ""),
        "dom_path": dom_path,
        "is_interactive": tag_name in INTERACTIVE_TAGS,
        "raw_attrs": {k: (v if isinstance(v, str) else " ".join(v)) for k, v in attrs.items()},
    }


def build_locator_from_element(features: Dict[str, Any]) -> str:
    """
    Generate the best Playwright CSS locator from element features.
    Priority: data-testid > data-qa > id > aria-label > name+type > class
    """
    if features.get("data_testid"):
        return f'[data-testid="{features["data_testid"]}"]'
    if features.get("data_qa"):
        return f'[data-qa="{features["data_qa"]}"]'
    if features.get("id"):
        return f'#{features["id"]}'
    if features.get("aria_label"):
        return f'[aria-label="{features["aria_label"]}"]'
    if features.get("name") and features.get("type"):
        return f'{features["tag_name"]}[name="{features["name"]}"]'
    if features.get("name"):
        return f'[name="{features["name"]}"]'
    if features.get("class_list"):
        cls = ".".join(features["class_list"][:2])  # max 2 classes
        return f'{features["tag_name"]}.{cls}'
    if features.get("text") and features.get("tag_name"):
        return f'{features["tag_name"]}:has-text("{features["text"][:50]}")'
    return features.get("tag_name", "unknown")
