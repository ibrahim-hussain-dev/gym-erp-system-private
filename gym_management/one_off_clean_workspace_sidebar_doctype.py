import frappe

def run():
    print("=" * 60)
    print("Workspace Sidebar records")
    print("=" * 60)
    sidebars = frappe.get_all("Workspace Sidebar", fields=["name"])
    print(sidebars)
    for s in sidebars:
        doc = frappe.get_doc("Workspace Sidebar", s.name)
        print(f"--- {s.name} ---")
        print(doc.as_dict())

    print()
    print("=" * 60)
    print("Workspace Sidebar Item records (all)")
    print("=" * 60)
    items = frappe.get_all("Workspace Sidebar Item", fields=["name", "parent", "parentfield", "parenttype"])
    for i in items:
        doc = frappe.get_doc("Workspace Sidebar Item", i.name)
        print(f"{i.name} | parent={i.parent} | {doc.as_dict()}")
