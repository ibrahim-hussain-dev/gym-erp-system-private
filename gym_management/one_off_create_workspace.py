import frappe
import json

def run():
    if frappe.db.exists("Workspace", "Gym Operations"):
        print("Already exists, skipping creation.")
        return

    content = [
        {"id": "header-gym-1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Gym Operations</b></span>", "col": 12}}
    ]

    ws = frappe.get_doc({
        "doctype": "Workspace",
        "title": "Gym Operations",
        "label": "Gym Operations",
        "module": "Gym-ERP-System",
        "public": 1,
        "is_hidden": 0,
        "icon": "tool",
        "indicator_color": "blue",
        "content": json.dumps(content),
        "sequence_id": 99.0,
    })
    ws.flags.ignore_permissions = True
    ws.insert()
    frappe.db.commit()
    print("Created Workspace:", ws.name)
