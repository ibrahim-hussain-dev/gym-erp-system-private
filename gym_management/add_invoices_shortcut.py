import frappe


def _add_shortcut_if_missing(workspace_name, label, doctype_link):
    if not frappe.db.exists("Workspace", workspace_name):
        print(f"  Workspace '{workspace_name}' not found, skipping")
        return
    doc = frappe.get_doc("Workspace", workspace_name)
    existing = [s.link_to for s in doc.shortcuts if s.link_to == doctype_link]
    if existing:
        print(f"  '{workspace_name}': shortcut for '{doctype_link}' already exists - OK")
        return
    doc.append("shortcuts", {
        "type": "DocType",
        "link_to": doctype_link,
        "label": label,
        "doc_view": "List",
    })
    doc.save(ignore_permissions=True)
    print(f"  FIXED: added '{label}' shortcut (-> {doctype_link}) to workspace '{workspace_name}'")


def run():
    print("=" * 80)
    print("Adding 'Gym Invoices' shortcut (-> Sales Invoice) to Impact Health Studio and Front Desk workspaces")
    print("=" * 80)
    for ws in ["Impact Health Studio", "Front Desk"]:
        _add_shortcut_if_missing(ws, "Gym Invoices", "Sales Invoice")

    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("VERIFICATION")
    for ws in ["Impact Health Studio", "Front Desk"]:
        if frappe.db.exists("Workspace", ws):
            doc = frappe.get_doc("Workspace", ws)
            labels = [s.label for s in doc.shortcuts]
            print(f"  {ws} shortcuts:", labels)

    print()
    print("DONE.")
    print("=" * 80)
