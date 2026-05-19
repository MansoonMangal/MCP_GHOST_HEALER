import os
import re
import logging

logger = logging.getLogger("SourceHealer")

class SourceHealer:
    """
    👻 SourceHealer — Dynamically patches Python source code files on disk
    by replacing old broken locators with successfully healed ones.
    """
    @staticmethod
    def apply_fix(file_path: str, line_number: int, old_locator: str, new_locator: str) -> bool:
        print(f"[GHOST] [SourceHealer] apply_fix called for {file_path}:{line_number} | old: {old_locator} | new: {new_locator}")
        if not file_path or not os.path.exists(file_path):
            print(f"[GHOST] [SourceHealer] File not found or empty: {file_path}")
            logger.error(f"[GHOST] [SourceHealer] File not found: {file_path}")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            fixed = False
            fixed_line = line_number

            clean_old = old_locator
            clean_new = new_locator
            if old_locator.startswith("#") and new_locator.startswith("#"):
                clean_old = old_locator[1:]
                clean_new = new_locator[1:]
            elif old_locator.startswith(".") and new_locator.startswith("."):
                clean_old = old_locator[1:]
                clean_new = new_locator[1:]

            options = [
                (old_locator, new_locator),
                (clean_old, clean_new)
            ]

            # Try extracting from *[id="..."] and *[class="..."]
            id_match = re.match(r'^\*\[id="(.+?)"\]$', old_locator)
            if id_match:
                raw_id = id_match.group(1)
                healed_id = new_locator[1:] if new_locator.startswith("#") else new_locator
                options.append((raw_id, healed_id))
            class_match = re.match(r'^\*\[class="(.+?)"\]$', old_locator)
            if class_match:
                raw_class = class_match.group(1)
                healed_class = new_locator[1:] if new_locator.startswith(".") else new_locator
                options.append((raw_class, healed_class))

            for old_s, new_s in options:
                if fixed:
                    break

                # 1. Try to patch the specific line
                if 0 < line_number <= len(lines):
                    orig_line = lines[line_number - 1]
                    escaped_old = re.escape(old_s)
                    upd_line = re.sub(f"(['\"]){escaped_old}(['\"])", f"\\1{new_s}\\2", orig_line)
                    if upd_line == orig_line:
                        upd_line = orig_line.replace(old_s, new_s)
                    
                    if upd_line != orig_line:
                        lines[line_number - 1] = upd_line
                        fixed = True
                        break

                # 2. Fallback scan if the specific line wasn't patched
                if not fixed:
                    escaped_old = re.escape(old_s)
                    for idx, line in enumerate(lines):
                        if old_s in line:
                            upd_line = re.sub(f"(['\"]){escaped_old}(['\"])", f"\\1{new_s}\\2", line)
                            if upd_line == line:
                                upd_line = line.replace(old_s, new_s)
                            if upd_line != line:
                                lines[idx] = upd_line
                                fixed_line = idx + 1
                                fixed = True
                                break

            if fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                print(f"[GHOST] [SourceHealer] Patched successfully at line {fixed_line}!")
                logger.info(f"[GHOST] 📝 SourceHealer patching: {os.path.basename(file_path)}:{fixed_line}")
                logger.info(f"         OLD → '{old_locator}'")
                logger.info(f"         NEW → '{new_locator}'")
                logger.info(f"[GHOST] ✅ Source permanently fixed.\n")
                return True
            else:
                print(f"[GHOST] [SourceHealer] Could not match selector options in {file_path}")
                logger.error(f"[GHOST] [SourceHealer] Could not locate '{old_locator}' in {file_path}")
                return False
        except Exception as e:
            print(f"[GHOST] [SourceHealer] Exception: {e}")
            logger.error(f"[GHOST] [SourceHealer] Patching failed: {e}")
            return False

source_healer = SourceHealer()
