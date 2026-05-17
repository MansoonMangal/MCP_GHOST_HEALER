import inspect
import os
from typing import Optional, Tuple

def parse_stack_trace() -> Tuple[Optional[str], Optional[int]]:
    """
    Walk the call stack to find the user's test file that triggered the action.
    Returns (filename, line_number)
    """
    stack = inspect.stack()
    for frame in stack:
        filename = frame.filename
        
        # Ignore framework internals
        if (
            "ghost_healer" not in filename
            and "site-packages" not in filename
            and "playwright" not in filename
            and "selenium" not in filename
            and filename.endswith((".py", ".ts", ".js", ".java"))
            and os.path.exists(filename)
        ):
            return filename, frame.lineno
            
    return None, None
