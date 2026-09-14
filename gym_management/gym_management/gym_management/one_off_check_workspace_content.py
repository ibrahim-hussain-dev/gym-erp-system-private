import frappe
import json

def run():
    ws = frappe.get_doc("Workspace", "Impact Health Studio")
    content = json.loads(ws.content) if isinstance(ws.content, str) else ws.content
    for block in content:
        data = block.get("data", {})
        label = data.get("shortcut_name") or data.get("card_name") or data.get("text") or ""
        if "PT" in str(label) or "pt" in str(block.get("type","")):
            print(block)
    print("")
    print("=== Full shortcut list ===")
    for s in ws.shortcuts:
        print(s.label, "|", s.link_to, "|", s.type)
