from __future__ import annotations
import os
import re
from config import Config


def extract_file_from_traceback(traceback: str) -> tuple[str | None, str | None]:
    """Extract file path and line number from a Python traceback."""
    match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+)', traceback)
    if match:
        return match.group(1), match.group(2)
    return None, None


def read_file(file_path: str, max_lines: int = 50) -> str:
    """Read a file and return its content, with line numbers, up to max_lines."""
    if not os.path.exists(file_path):
        addons_base = Config.ODOO_ADDONS_PATH
        if addons_base:
            full_path = os.path.join(addons_base, file_path)
            if os.path.exists(full_path):
                file_path = full_path
            else:
                return f"[File not found: {file_path}]"
        else:
            return f"[File not found: {file_path}]"

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        numbered = []
        for i, line in enumerate(lines[:max_lines], 1):
            numbered.append(f"{i:4d} | {line.rstrip()}")
        return "\n".join(numbered)
    except Exception as e:
        return f"[Error reading file: {e}]"
