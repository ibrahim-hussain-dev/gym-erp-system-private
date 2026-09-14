import frappe
import json

def run():
    meta = frappe.get_meta("Workspace")
    print("=== Workspace meta: title-related fields ===")
    print("title_field (meta):", meta.get("title_field"))
    for f in meta.fields:
        if "title" in f.fieldname.lower() or "label" in f.fieldname.lower():
            print(f.fieldname, "|", f.fieldtype)

    doc = frappe.get_doc("Workspace", "Gym Operations")
    print("\n=== Full doc dict (content trimmed) ===")
    d = doc.as_dict()
    d.pop("content", None)
    print(json.dumps(d, indent=2, default=str))
