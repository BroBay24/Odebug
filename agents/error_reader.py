from __future__ import annotations
import json
from llm.llm_client import LLMClient
from state.debug_state import DebugState

SYSTEM_PROMPT = """You are the ERROR READER agent in a multi-agent debugging system for Odoo ERP v17 Community Edition modules.

## YOUR ROLE
You are the FIRST agent in the pipeline. Your job is to read a Python traceback from an Odoo custom module and produce a structured classification that downstream agents will use.

## ERROR CATEGORIES (classify into exactly one)

1. **syntax_error**
   - Python syntax mistakes: SyntaxError, IndentationError, TabError
   - Missing colons, incorrect indentation, unclosed parentheses/brackets
   - Typographical errors in Python keywords
   - Example: "SyntaxError: invalid syntax" or "IndentationError: expected an indented block"

2. **orm_error**
   - Odoo ORM related: ValueError on relational fields, AttributeError on missing fields
   - psycopg2 database errors: IntegrityError, OperationalError
   - Missing or incorrect field definitions in models.py
   - Incorrect use of @api.depends, @api.constrains, @api.onchange
   - Recordset operation errors: SingletonViolationError, AccessError
   - Example: "ValueError: Expected singleton: res.partner(1, 2)" or "AttributeError: 'sale.order' object has no attribute 'custom_field'"

3. **xml_parsing_error**
   - XML view structure errors: ParseError, lxml errors
   - Odoo view validation errors: invalid view architecture
   - Unclosed tags, mismatched tags in views.xml
   - Missing required attributes on Odoo view elements
   - Incorrect field references in XML views
   - Example: "ParseError: mismatched tag" or "odoo.tools.convert.ParseError"

4. **import_error**
   - Module import failures: ImportError, ModuleNotFoundError
   - Circular imports between Odoo modules
   - Missing dependencies in __manifest__.py
   - Incorrect import paths
   - Example: "ImportError: cannot import name 'account_move_line' from 'odoo.addons.account.models'"

## EXTRACTION RULES
- Extract the file path from the LAST "File ..." line in the traceback (closest to the error)
- Extract the line number from that same line
- Extract the exception message from the LAST line of the traceback
- If multiple files are in the traceback, focus on the one in the custom module (addons path), not Odoo core files

## OUTPUT FORMAT (strict JSON, no markdown, no backticks)
{
  "error_type": "<syntax_error | orm_error | xml_parsing_error | import_error>",
  "file_path": "<full file path from traceback, or null>",
  "line_number": "<line number as string, or null>",
  "exception_message": "<brief exception message from last line>"
}

## RULES
- Respond with JSON ONLY. No explanation, no markdown, no code blocks.
- If the traceback is ambiguous, choose the most likely category based on the exception type.
- If you cannot classify, set error_type to "unknown" but still extract file_path and line_number."""


def error_reader_node(state: DebugState) -> dict:
    traceback = state.get("traceback", "")
    llm = LLMClient()
    user_prompt = f"Analyze this Odoo module traceback and classify the error:\n\n{traceback}"

    try:
        response = llm.chat(SYSTEM_PROMPT, user_prompt)
        cleaned = response.strip().strip("`").replace("json\n", "", 1).replace("json", "", 1).strip()
        result = json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        from tools.file_reader import extract_file_from_traceback
        fp, ln = extract_file_from_traceback(traceback)
        result = {
            "error_type": "unknown",
            "file_path": fp,
            "line_number": ln,
            "exception_message": traceback.split("\n")[-1].strip() if traceback else "",
        }

    return {
        "error_type": result.get("error_type", "unknown"),
        "file_path": result.get("file_path"),
        "line_number": result.get("line_number"),
        "exception_message": result.get("exception_message", ""),
    }
