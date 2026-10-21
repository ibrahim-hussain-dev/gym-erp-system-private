import frappe
import json


def run():
    for name in ["Impact Health Studio", "Front Desk"]:
        if not frappe.db.exists("Workspace Sidebar", name):
            print(f"--- Workspace Sidebar '{name}': DOES NOT EXIST ---")
            continue
        doc = frappe.get_doc("Workspace Sidebar", name)
        print(f"=== Workspace Sidebar: {name} ===")
        as_dict = doc.as_dict()
        for key, value in as_dict.items():
            if key in ("items", "creation", "modified", "owner", "modified_by", "docstatus", "idx"):
                continue
            print(f"  {key}: {value!r}")
        print()

    print("=== Standard Workspace doctype (icon field) ===")
    for name in ["Impact Health Studio", "Front Desk"]:
        if frappe.db.exists("Workspace", name):
            icon = frappe.db.get_value("Workspace", name, "icon")
            print(f"  Workspace '{name}': icon={icon!r}")
        else:
            print(f"  Workspace '{name}': does not exist")
