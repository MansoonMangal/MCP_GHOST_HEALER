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

            lines[line_number - 1] = new_line

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
            logger.info(f"✨ [FIXED] {file_path}:{line_number} | {old_locator} -> {new_locator}")
            return True
        except Exception as e:
            logger.error(f"Failed to fix source: {e}")
            return False

source_healer = UniversalSourceHealer()
