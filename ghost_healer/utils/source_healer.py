"""
Ghost Healer — AST-Safe Source Healer

Permanently rewrites test source files when a locator is healed.
Uses libcst for Python (safe AST rewriting) and regex for TS/Java/JS.

Why AST over regex?
  Regex patching is fragile — it can corrupt multi-line strings or
  match selectors inside comments. libcst parses the file into a
  Concrete Syntax Tree and replaces only real string literals.
"""
import os
import re
import inspect
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("GhostSourceHealer")


# ── Python AST Patching (libcst) ──────────────────────────────────────────────

def _patch_python_ast(file_path: str, old_selector: str, new_selector: str) -> bool:
    """
    Use libcst to safely rewrite a Python file.
    Only replaces exact string literals matching old_selector.
    Returns True if any replacement was made.
    """
    try:
        import libcst as cst

        class SelectorRewriter(cst.CSTTransformer):
            def __init__(self):
                self.changed = False

            def leave_SimpleString(self, original_node, updated_node):
                raw = updated_node.value
                # Strip quotes to get the inner value
                inner = raw[1:-1] if len(raw) >= 2 else raw
                if inner == old_selector:
                    new_raw = raw[0] + new_selector + raw[-1]
                    self.changed = True
                    return updated_node.with_changes(value=new_raw)
                return updated_node

            def leave_FormattedStringText(self, original_node, updated_node):
                if old_selector in updated_node.value:
                    self.changed = True
                    return updated_node.with_changes(
                        value=updated_node.value.replace(old_selector, new_selector)
                    )
                return updated_node

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = cst.parse_module(source)
        rewriter = SelectorRewriter()
        new_tree = tree.visit(rewriter)

        if rewriter.changed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_tree.code)
            return True

        return False

    except ImportError:
        logger.warning("libcst not installed — falling back to regex patching for Python.")
        return _patch_regex(file_path, old_selector, new_selector)
    except Exception as e:
        logger.warning(f"libcst parsing failed ({e}) — falling back to regex.")
        return _patch_regex(file_path, old_selector, new_selector)


# ── Regex Patching (TS / JS / Java fallback) ──────────────────────────────────

def _patch_regex(file_path: str, old_selector: str, new_selector: str) -> bool:
    """
    Regex-based patching for TypeScript, JavaScript, and Java files.
    Also used as Python fallback when libcst is not available.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        old_escaped = re.escape(old_selector)
        # Match selector surrounded by any quote type
        pattern = rf"(['\"`]){old_escaped}(['\"`])"

        if not re.search(pattern, content):
            logger.warning(f"Selector '{old_selector}' not found in {file_path}")
            return False

        new_content = re.sub(pattern, rf"\g<1>{new_selector}\g<2>", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True

    except Exception as e:
        logger.error(f"Regex patching failed for {file_path}: {e}")
        return False


# ── Stack Tracer ──────────────────────────────────────────────────────────────

def _find_caller_file() -> Optional[str]:
    """Walk the call stack to find the test file that triggered the healing."""
    stack = inspect.stack()
    for frame in stack:
        filename = frame.filename
        # Skip framework internals
        if (
            "ghost_healer" not in filename
            and "site-packages" not in filename
            and filename.endswith((".py", ".ts", ".js", ".java"))
            and os.path.exists(filename)
        ):
            return filename
    return None


# ── Main SourceHealer Class ───────────────────────────────────────────────────

class SourceHealer:
    """
    👻 THE GHOST PATCHER

    Permanently rewrites source code files when a locator is healed.
    - Python files: uses libcst (AST-safe, no false positives)
    - TS/JS/Java files: uses regex with quote awareness
    """

    def apply_fix(
        self,
        old_selector: str,
        new_selector: str,
        file_path: Optional[str] = None,
    ) -> bool:
        """
        Find and rewrite the test file containing old_selector.

        Args:
            old_selector: The broken locator to replace.
            new_selector: The healed locator to write in.
            file_path:    Optional explicit file path (skips stack detection).

        Returns:
            True if the file was successfully patched, False otherwise.
        """
        target = file_path or _find_caller_file()

        if not target or not os.path.exists(target):
            logger.warning(
                f"[SourceHealer] Could not locate source file for '{old_selector}'"
            )
            return False

        suffix = Path(target).suffix.lower()
        logger.info(
            f"[SourceHealer] Patching {Path(target).name} "
            f"({suffix}) — '{old_selector}' → '{new_selector}'"
        )

        if suffix == ".py":
            patched = _patch_python_ast(target, old_selector, new_selector)
        else:
            # TypeScript (.ts), JavaScript (.js), Java (.java)
            patched = _patch_regex(target, old_selector, new_selector)

        if patched:
            logger.info(f"[SourceHealer] ✅ Patched: {Path(target).name}")
        else:
            logger.warning(
                f"[SourceHealer] No changes made to {Path(target).name}"
            )

        return patched


# Global instance
source_healer = SourceHealer()
