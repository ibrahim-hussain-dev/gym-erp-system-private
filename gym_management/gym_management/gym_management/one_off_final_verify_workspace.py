import frappe
import json

def run():
    doc = frappe.get_doc("Workspace", "Gym Operations")
    print("Shortcuts count:", len(doc.shortcuts))
    print("Shortcut labels:", [r.label for r in doc.shortcuts])
    print("Links count:", len(doc.links))
    print()
    content = json.loads(doc.content or "[]")
    print("Content blocks count:", len(content))
    bad = [b for b in content if "manage" in json.dumps(b).lower() or "membership retention" in json.dumps(b).lower()]
    print("Any block still mentioning manage-subscription / Membership Retention:", bad)
