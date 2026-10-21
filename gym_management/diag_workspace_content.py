import frappe
import json


def run():
    for ws_name in ["Impact Health Studio", "Front Desk"]:
        print("=" * 80)
        print(f"Workspace: {ws_name}")
        print("=" * 80)
        if not frappe.db.exists("Workspace", ws_name):
            print("  not found")
            continue
        doc = frappe.get_doc("Workspace", ws_name)
        print("STEP 1: raw 'content' field (this drives the page layout / sidebar list)")
        try:
            content = json.loads(doc.content) if doc.content else []
            print(json.dumps(content, indent=2))
        except Exception as e:
            print("  could not parse content as JSON:", e)
            print("  raw content:", doc.content)

        print()
        print("STEP 2: 'links' child table rows (Workspace Link)")
        for l in doc.links:
            print("  ", l.as_dict())

        print()
        print("STEP 3: child Workspace docs with parent_page = this workspace")
        children = frappe.get_all(
            "Workspace",
            filters={"parent_page": ws_name},
            fields=["name", "label", "title", "type", "link_to", "public", "is_hidden", "idx"],
            order_by="idx asc",
        )
        for c in children:
            print("  ", c)
        print()

    print("DONE.")
