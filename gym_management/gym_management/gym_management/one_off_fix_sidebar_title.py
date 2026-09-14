import frappe
import json

def run():
    print("=== Workspace Sidebar meta (title/label fields) ===")
    meta = frappe.get_meta("Workspace Sidebar")
    for f in meta.fields:
        if "title" in f.fieldname.lower() or "label" in f.fieldname.lower():
            print(f.fieldname, "|", f.fieldtype)

    doc = frappe.get_doc("Workspace Sidebar", "Gym Operations")
    d = doc.as_dict()
    print("\n=== Workspace Sidebar 'Gym Operations' doc ===")
    print(json.dumps(d, indent=2, default=str))

    updated = []
    for fieldname in ["title", "label"]:
        if fieldname in d:
            frappe.db.set_value("Workspace Sidebar", "Gym Operations", fieldname, "Impact Health Studio")
            updated.append(fieldname)
    frappe.db.commit()
    print("\nUpdated fields on Workspace Sidebar:", updated)

    frappe.db.set_value("Workspace", "Gym Operations", "label", "Impact Health Studio")
    frappe.db.set_value("Workspace", "Gym Operations", "title", "Impact Health Studio")
    frappe.db.commit()

    frappe.clear_cache()
    print("DONE")
