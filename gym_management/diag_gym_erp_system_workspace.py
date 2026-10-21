import json

import frappe


def run():
    print("=" * 80)
    print("Gym-ERP-System workspace diagnostic")
    print("=" * 80)

    if not frappe.db.exists("Workspace", "Gym-ERP-System"):
        print("Workspace 'Gym-ERP-System' does not exist.")
        return

    doc = frappe.get_doc("Workspace", "Gym-ERP-System")
    info = {
        "name": doc.name,
        "label": doc.label,
        "module": doc.module,
        "public": doc.public,
        "is_hidden": doc.is_hidden,
        "icon": doc.icon,
        "parent_page": doc.parent_page,
        "for_user": doc.for_user,
        "sequence_id": doc.sequence_id,
    }
    print(json.dumps(info, indent=2, default=str))

    print()
    print("--- other Workspace docs with parent_page = 'Gym-ERP-System' ---")
    print(frappe.get_all("Workspace", filters={"parent_page": "Gym-ERP-System"}, pluck="name"))

    print()
    print("--- all Workspace docs belonging to module 'Gym-ERP-System' ---")
    print(frappe.get_all("Workspace", filters={"module": "Gym-ERP-System"},
                          fields=["name", "public", "is_hidden", "icon", "parent_page"]))

    print()
    print("--- all Workspace docs in the whole site (name, module, public) ---")
    for w in frappe.get_all("Workspace", fields=["name", "module", "public", "is_hidden"], order_by="name"):
        print(f"  {w.name!r:35} module={w.module!r:25} public={w.public} is_hidden={w.is_hidden}")

    print()
    print("DONE.")
