import os
import re
import logging
from pathlib import Path

logger = logging.getLogger("UniversalHealer")

class UniversalSourceHealer:
    """
    Heals source code for ANY language (Python, Java, TS).
    """
    @staticmethod
    def apply_fix(file_path: str, line_number: int, old_locator: str, new_locator: str):
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line_number > len(lines):
                logger.error(f"Line number {line_number} out of range for {file_path}")
                return False

            target_line = lines[line_number - 1]
            
            # Smart Regex: Find the old locator inside the line and replace it
            # Escaping the old locator for regex safety
            escaped_old = re.escape(old_locator)
            new_line = re.sub(f"(['\"]){escaped_old}(['\"])", f"\\1{new_locator}\\2", target_line)

            if target_line == new_line:
                # Try a broader match if strict quoting fails (e.g. for CSS selectors with spaces)
                new_line = target_line.replace(old_locator, new_locator)

            if target_line != new_line:
                lines[line_number - 1] = new_line
                logger.info(f"✨ [FIXED] {file_path}:{line_number} | {old_locator} -> {new_locator}")
            else:
                # Fallback: Scan the entire file from top to bottom to locate constructor/declaration definitions
                found_and_patched = False
                for idx, line in enumerate(lines):
                    if old_locator in line:
                        patched_line = re.sub(f"(['\"]){escaped_old}(['\"])", f"\\1{new_locator}\\2", line)
                        if patched_line == line:
                            patched_line = line.replace(old_locator, new_locator)
                        lines[idx] = patched_line
                        line_number = idx + 1
                        found_and_patched = True
                        logger.info(f"✨ [SCAN-FIXED] {file_path}:{line_number} (constructor scan) | {old_locator} -> {new_locator}")
                        break
                
                if not found_and_patched:
                    logger.error(f"Could not locate '{old_locator}' anywhere in {file_path}")
                    return False

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            logger.error(f"Failed to fix source: {e}")
            return False

source_healer = UniversalSourceHealer()
