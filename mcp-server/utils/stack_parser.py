import re
from typing import Optional, Tuple

class StackParser:
    """
    Parses stack traces from multiple languages to extract file and line info.
    """
    @staticmethod
    def parse(stack_trace: str) -> Tuple[Optional[str], Optional[int]]:
        if not stack_trace:
            return None, None

        # Find all potential file:line matches
        # TS/JS: path:line:col
        ts_matches = re.finditer(r"([a-zA-Z]:.*?\.(?:ts|js)):(\d+):", stack_trace)
        for m in ts_matches:
            file_path, line_num = m.group(1), int(m.group(2))
            if "HealQA" not in file_path and "node_modules" not in file_path:
                return file_path, line_num

        # Java: (File.java:line)
        java_matches = re.finditer(r"\((.*?\.java):(\d+)\)", stack_trace)
        for m in java_matches:
            file_path, line_num = m.group(1), int(m.group(2))
            if "GhostHealer" not in file_path: # Skip framework if any
                return file_path, line_num

        # Python: File "...", line ...
        py_matches = re.finditer(r'File "(.*\.py)", line (\d+)', stack_trace)
        for m in py_matches:
            file_path, line_num = m.group(1), int(m.group(2))
            if "ghost_framework" not in file_path and "conftest" not in file_path:
                return file_path, line_num

        return None, None

stack_parser = StackParser()
