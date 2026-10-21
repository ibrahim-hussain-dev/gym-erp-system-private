import frappe
import json

def run():
    doc = frappe.get_doc("Workspace", "Gym Operations")
    valid_labels = {row.label for row in doc.shortcuts}
    print("Valid shortcut labels currently in shortcuts table:", valid_labels)

    content = json.loads(doc.content or "[]")
    before = len(content)
    cleaned = []
    removed = []
    for block in content:
        if block.get("type") == "shortcut":
            name = block.get("data", {}).get("shortcut_name")
            if name not in valid_labels:
                removed.append(name)
                continue
        cleaned.append(block)

    doc.content = json.dumps(cleaned)
    doc.flags.ignore_links = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    print(f"Content blocks before={before} after={len(cleaned)}")
    print("Removed orphaned shortcut blocks:", removed)
