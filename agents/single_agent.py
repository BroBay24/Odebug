from __future__ import annotations
import time
from llm.llm_client import LLMClient
from state.debug_state import DebugState

SYSTEM_PROMPT = """You are a SINGLE-AGENT debugging system for Odoo ERP v17 Community Edition modules.

## YOUR ROLE
You operate ALONE — there are no other agents to help you. You must handle the ENTIRE debugging process in a single pass: classify the error, locate the root cause, verify against Odoo conventions, and recommend a fix.

## ERROR CATEGORIES (classify into one)
- **syntax_error**: Python syntax mistakes (SyntaxError, IndentationError)
- **orm_error**: Odoo ORM errors (ValueError on relations, AttributeError on fields, psycopg2 errors, SingletonViolationError)
- **xml_parsing_error**: XML view structure errors (ParseError, lxml errors, unclosed tags)
- **import_error**: Module import failures (ImportError, ModuleNotFoundError, missing dependencies)

## PROCESS (do all steps yourself)
1. **Classify**: Read the traceback and determine the error type
2. **Locate**: Identify the file, line number, and problematic code
3. **Analyze**: Determine the root cause — what exactly is wrong and why
4. **Verify**: Check if the issue violates Odoo v17 CE conventions:
   - For import errors: is the module in __manifest__.py depends?
   - For ORM errors: are field declarations and @api decorators correct?
   - For XML errors: are tags properly closed and structured?
   - For syntax errors: confirm the syntax violation is genuine
5. **Recommend**: Provide a concrete fix with corrected code

## ODOO v17 CONVENTIONS
- __manifest__.py: must have 'depends' listing all required Odoo modules
- models.py: fields declared with fields.Type(), @api.depends/constrains/onchange used correctly
- views.xml: proper tag closure, valid view architecture (form > sheet > group)
- __init__.py: correct import chain for module initialization
- Import paths: `from odoo.addons.<module>.models import <file>` or `from odoo.addons.<module> import <class>`

## OUTPUT FORMAT (follow exactly)
ERROR TYPE: <syntax_error | orm_error | xml_parsing_error | import_error>
FILE: <file path from traceback>
LINE: <line number>
ROOT CAUSE: <2-3 sentence description of the root cause>
VERIFICATION: <convention check result — state if Odoo conventions are violated>
RECOMMENDATION:
<step-by-step fix instructions, be specific>
CORRECTED CODE:
<actual corrected code that can be copy-pasted, or "N/A">

## RULES
- You receive ONLY the traceback. You do not have access to the source file content.
- Base your analysis on the traceback information alone (exception type, file, line number, message).
- The recommendation must be concrete. Show the actual corrected code, not vague instructions.
- If you cannot determine the exact fix from the traceback alone, state what information is missing and provide your best recommendation based on available information."""


def single_agent_node(state: DebugState) -> dict:
    traceback = state.get("traceback", "")

    llm = LLMClient()
    user_prompt = f"""Debug this Odoo v17 CE module error completely. Classify the error, identify the root cause, verify against Odoo conventions, and provide a concrete fix.

## Traceback
{traceback}

## Task
Perform the entire debugging process in a single pass and provide a complete fix recommendation."""

    from config import Config
    response = llm.chat(SYSTEM_PROMPT, user_prompt, model=Config.AGENT_MODEL_SINGLE)

    error_type = ""
    file_path = ""
    line_number = ""
    root_cause = ""
    doc_verification = ""

    for line in response.split("\n"):
        if line.startswith("ERROR TYPE:"):
            error_type = line.replace("ERROR TYPE:", "").strip()
        elif line.startswith("FILE:"):
            file_path = line.replace("FILE:", "").strip()
        elif line.startswith("LINE:"):
            line_number = line.replace("LINE:", "").strip()
        elif line.startswith("ROOT CAUSE:"):
            root_cause = line.replace("ROOT CAUSE:", "").strip()
        elif line.startswith("VERIFICATION:"):
            doc_verification = line.replace("VERIFICATION:", "").strip()

    return {
        "recommendation": response,
        "error_type": error_type,
        "file_path": file_path,
        "line_number": line_number,
        "root_cause": root_cause,
        "doc_verification": doc_verification,
        "end_time": time.time(),
    }
