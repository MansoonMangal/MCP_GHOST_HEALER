import inspect
import os
from typing import Optional, Tuple

def parse_stack_trace() -> Tuple[Optional[str], Optional[int]]:
    stack = inspect.stack()
    for frame in stack:
        filename = frame.filename
        abs_filename = os.path.abspath(filename)
        print(f"[GHOST] [DEBUG] Frame: {filename} | abs: {abs_filename} | exists: {os.path.exists(abs_filename)}")
        
        # Ignore framework internals
        # Note: we check if "ghost_healer" is in the relative file path to avoid excluding the whole project path!
        # If the filename contains "ghost_healer" as a module directory (e.g. "ghost_healer/adapters/" or "ghost_healer/core/"), we ignore it.
        # But we shouldn't ignore it if "ghost_healer" is just part of the folder prefix of the workspace path!
        # So we check if the relative path within workspace contains "ghost_healer".
        is_internal = False
        normalized_filename = filename.replace("\\", "/")
        if "ghost_healer/adapters" in normalized_filename or "ghost_healer/core" in normalized_filename or "ghost_healer/utils" in normalized_filename:
            is_internal = True
            
        if (
            not is_internal
            and "site-packages" not in normalized_filename
            and "selenium/webdriver" not in normalized_filename
            and "playwright/" not in normalized_filename
            and normalized_filename.endswith((".py", ".ts", ".js", ".java"))
            and os.path.exists(abs_filename)
        ):
            return abs_filename, frame.lineno
            
    return None, None
