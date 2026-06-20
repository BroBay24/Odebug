from __future__ import annotations
from typing import TypedDict, Optional


class DebugState(TypedDict, total=False):
    traceback: str
    error_type: str
    file_path: str
    line_number: str
    exception_message: str
    code_snippet: str
    root_cause: str
    layer: str
    doc_verification: str
    doc_notes: str
    recommendation: str
    start_time: float
    end_time: float
    retry_count: int
