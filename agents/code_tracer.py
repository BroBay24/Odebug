from __future__ import annotations
from llm.llm_client import LLMClient
from tools.file_reader import read_file
from state.debug_state import DebugState

SYSTEM_PROMPT = """You are the CODE TRACER agent in a multi-agent debugging system for Odoo ERP v17 Community Edition modules.

## YOUR ROLE
You are the SECOND agent in the pipeline. The Error Reader has already classified the error and identified the file. Your job is to read the actual source code, analyze the problematic area, and identify the root cause.

## ODOO MODULE LAYERS (identify which layer is affected)
- **models.py** — ORM layer: field definitions, business logic, @api decorators, model classes
- **views.xml** — Presentation layer: form views, tree views, kanban, search, QWeb templates
- **__manifest__.py** — Config layer: module metadata, dependencies list, data files list
- **__init__.py** — Init layer: Python imports for module initialization
- **security/** — Access layer: CSV access rules, XML record rules
- **other** — Any other file

## ANALYSIS INSTRUCTIONS PER ERROR TYPE

### For syntax_error:
- Look at the exact line number indicated in the traceback
- Check for: missing colons, wrong indentation, unclosed brackets, typos in keywords
- Report the exact syntax violation

### For orm_error:
- Check field definitions: are fields declared with correct types (fields.Char, fields.Many2one, etc.)?
- Check relational fields: do Many2one/One2many/Many2many reference valid models?
- Check @api decorators: are they used correctly?
- Check recordset operations: is the code assuming a singleton when multiple records exist?
- Check SQL/ORM method calls: are search(), browse(), create() used with correct parameters?

### For xml_parsing_error:
- Check XML structure: are all tags properly closed?
- Check Odoo view elements: <form>, <tree>, <kanban>, <search>, <sheet>, <group>, <field>
- Check field references: do 'name' attributes match actual model fields?
- Check for missing required attributes on view elements

### For import_error:
- Check import statements: are they using correct Odoo import paths?
- Check __manifest__.py: is the imported module listed in 'depends'?
- Check for circular imports between modules
- Check __init__.py: are Python imports structured correctly?

## OUTPUT FORMAT (follow exactly)
ROOT CAUSE: <one to three sentences describing the exact root cause of the error>
LAYER: <models.py | views.xml | __manifest__.py | __init__.py | security/ | other>
CODE SNIPPET: <the specific code lines that are problematic, including line numbers if visible>

## RULES
- Be specific about the root cause. Do not say "there is an error" — explain WHAT is wrong and WHY.
- The CODE SNIPPET should contain the actual problematic lines, not the entire file.
- If the file content is not available, state what you expected to find and what the traceback indicates."""


def code_tracer_node(state: DebugState) -> dict:
    file_path = state.get("file_path", "")
    line_number = state.get("line_number", "")
    error_type = state.get("error_type", "")
    exception_msg = state.get("exception_message", "")
    traceback = state.get("traceback", "")

    file_content = read_file(file_path) if file_path else "[No file path available]"

    llm = LLMClient()
    user_prompt = f"""## Context from Error Reader
Error type: {error_type}
File: {file_path}
Line: {line_number}
Exception: {exception_msg}

## Original Traceback
{traceback}

## Source File Content
{file_content}

## Task
Analyze the code at the indicated location and identify the root cause of the {error_type}."""

    from config import Config
    response = llm.chat(SYSTEM_PROMPT, user_prompt, model=Config.AGENT_MODEL_CODE_TRACER)

    root_cause = ""
    layer = ""
    code_snippet = ""
    for line in response.split("\n"):
        if line.startswith("ROOT CAUSE:"):
            root_cause = line.replace("ROOT CAUSE:", "").strip()
        elif line.startswith("LAYER:"):
            layer = line.replace("LAYER:", "").strip()
        elif line.startswith("CODE SNIPPET:"):
            code_snippet = line.replace("CODE SNIPPET:", "").strip()

    if not root_cause:
        root_cause = response[:300]
    if not code_snippet:
        code_snippet = file_content[:500] if file_content != "[No file path available]" else ""

    return {
        "root_cause": root_cause,
        "layer": layer,
        "code_snippet": code_snippet,
    }
