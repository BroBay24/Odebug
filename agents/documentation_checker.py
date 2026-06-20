from __future__ import annotations
from llm.llm_client import LLMClient
from tools.doc_checker import check_odoo_convention
from state.debug_state import DebugState

SYSTEM_PROMPT = """You are the DOCUMENTATION CHECKER agent in a multi-agent debugging system for Odoo ERP v17 Community Edition modules.

## YOUR ROLE
You are the THIRD agent in the pipeline. The Error Reader has classified the error and the Code Tracer has identified the root cause. Your job is to VERIFY these findings against Odoo v17 CE framework conventions and documentation.

## ODOO v17 CONVENTIONS TO CHECK

### For import_error:
1. **__manifest__.py depends**: The imported module MUST be listed in the 'depends' array. If missing, this is a convention violation.
2. **Import path format**: Odoo imports should follow the pattern `from odoo.addons.<module_name>.models import <file>` or `from odoo.addons.<module_name> import <model>`.
3. **__init__.py chain**: Each module's __init__.py must import its subdirectories. Models must be imported in __init__.py.
4. **Circular dependency**: Check if module A imports from module B while module B depends on module A.

### For orm_error:
1. **Field declaration**: Fields must be declared as class attributes using fields.Char(), fields.Many2one(), fields.One2many(), fields.Many2many(), etc.
2. **@api decorators**: @api.depends must list actual field names. @api.constrains must reference fields in the function signature. @api.onchange must reference fields that trigger the change.
3. **Recordset operations**: search() returns a recordset (may contain multiple records). Operations like field access on a multi-record recordset may cause SingletonViolationError.
4. **Model naming**: Models must use _name = 'model.name' with dot notation. _inherit must reference existing models.
5. **ORM methods**: create(), write(), unlink(), search(), browse() — verify correct parameter usage.

### For xml_parsing_error:
1. **View architecture**: Odoo views must follow valid structure: <form> > <sheet> > <group>, <tree> with <field> children, etc.
2. **Tag closure**: All XML tags must be properly closed. Self-closing tags need />.
3. **Required attributes**: <field name="..."> requires a 'name' attribute matching a model field. <record model="..."> requires a 'model' attribute.
4. **View types**: Form views, tree/list views, kanban views, search views each have specific required elements.

### For syntax_error:
1. **Python syntax**: Verify the specific syntax violation identified by Code Tracer.
2. **Odoo-specific patterns**: Some Odoo patterns look unusual but are valid (e.g., _name = 'model.name', _description = 'Model Description').
3. **Confirm**: Simply confirm the syntax error is genuine and not a false positive from Odoo's metaprogramming.

## OUTPUT FORMAT (follow exactly)
VERIFIED: <yes | no | partially>
NOTES: <list specific convention violations found, or "No convention violations detected. Findings are consistent with Odoo v17 CE conventions.">

## RULES
- "yes" = findings are correct and consistent with Odoo conventions
- "no" = findings contain errors or violate Odoo conventions (specify what is wrong)
- "partially" = some findings are correct but some need correction
- Be specific in NOTES. If you say "no", explain what is incorrect so the Code Tracer can retry.
- If you find that the root cause identified by Code Tracer is wrong or incomplete, state clearly what the correct root cause should be."""


def documentation_checker_node(state: DebugState) -> dict:
    error_type = state.get("error_type", "")
    file_path = state.get("file_path", "")
    code_snippet = state.get("code_snippet", "")
    root_cause = state.get("root_cause", "")

    conv = check_odoo_convention(error_type, file_path, code_snippet)

    llm = LLMClient()
    user_prompt = f"""## Context from Previous Agents
Error type: {error_type}
File: {file_path}
Root cause (from Code Tracer): {root_cause}
Code snippet (from Code Tracer): {code_snippet}

## Automated Convention Check (preliminary)
{conv}

## Task
Verify the above findings against Odoo v17 Community Edition conventions. Check if the root cause and code analysis are correct according to Odoo framework standards."""

    response = llm.chat(SYSTEM_PROMPT, user_prompt)

    verified = ""
    notes = ""
    for line in response.split("\n"):
        if line.startswith("VERIFIED:"):
            verified = line.replace("VERIFIED:", "").strip()
        elif line.startswith("NOTES:"):
            notes = line.replace("NOTES:", "").strip()

    if not verified:
        verified = "unknown"
    if not notes:
        notes = response[:300]

    return {
        "doc_verification": verified,
        "doc_notes": notes,
    }
