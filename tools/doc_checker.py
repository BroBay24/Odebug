from __future__ import annotations

ODOO_MANIFEST_FIELDS = ["name", "version", "depends", "data", "license", "author"]
ODOO_VIEW_TAGS = ["form", "tree", "kanban", "search", "calendar", "graph", "pivot"]
ODOO_ORM_METHODS = ["create", "write", "unlink", "search", "browse", "fields_get", "search_count"]


def check_odoo_convention(error_type: str, file_path: str, code_snippet: str) -> dict:
    """Check code against basic Odoo conventions. Returns dict with findings."""
    findings = {
        "manifest_check": None,
        "xml_check": None,
        "orm_check": None,
        "notes": [],
    }

    if file_path and "__manifest__" in file_path:
        if error_type == "import error":
            has_depends = "depends" in code_snippet if code_snippet else False
            findings["manifest_check"] = "depends field found" if has_depends else "depends field missing or incomplete"
            if not has_depends:
                findings["notes"].append("Module dependency may not be declared in __manifest__.py")

    if file_path and (file_path.endswith(".xml") or "views" in file_path):
        if error_type == "xml parsing error":
            for tag in ODOO_VIEW_TAGS:
                if f"<{tag}" in (code_snippet or "") and f"</{tag}>" not in (code_snippet or ""):
                    findings["xml_check"] = f"Unclosed <{tag}> tag detected"
                    findings["notes"].append(f"XML tag <{tag}> appears to be unclosed")

    if error_type == "orm error":
        for method in ODOO_ORM_METHODS:
            if method in (code_snippet or ""):
                findings["orm_check"] = f"ORM method '{method}' used"
        if not findings["orm_check"]:
            findings["orm_check"] = "No standard ORM method detected"

    return findings
