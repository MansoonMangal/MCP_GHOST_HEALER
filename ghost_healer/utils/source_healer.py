import os
import re
import inspect
import logging
from pathlib import Path

logger = logging.getLogger("SourceHealer")

class SourceHealer:
    """
    👻 THE GHOST PATCHER:
    Permanently rewrites source code files when a locator is healed.
    """
    @staticmethod
    def apply_fix(old_selector: str, new_selector: str):
        # 1. Trace the caller to find the test file
        stack = inspect.stack()
        test_file = None
        
        for frame in stack:
            # We look for a frame that isn't inside our framework
            filename = frame.filename
            if "ghost_healer" not in filename and filename.endswith(('.py', '.java', '.ts')):
                test_file = filename
                break
        
        if not test_file or not os.path.exists(test_file):
            logger.warning(f"Could not identify source file to patch for {old_selector}")
            return

        # 2. Perform the rewrite
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Escape quotes for regex
            old_esc = re.escape(old_selector)
            
            # Pattern matches the selector within quotes
            # Supports single, double, and template literal quotes
            pattern = rf"(['\"`]){old_esc}(['\"`])"
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, rf"\1{new_selector}\2", content)
                
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"🛡️ [PATCHED] {Path(test_file).name}: '{old_selector}' -> '{new_selector}'")
            else:
                logger.warning(f"Locator '{old_selector}' not found in {test_file} for patching.")
                
        except Exception as e:
            logger.error(f"Source patching failed: {e}")

# Global instance
source_healer = SourceHealer()
