import frappe


def run():
    print("=" * 80)
    print("STEP 1: ALL 'Workspace Sidebar' records (title, for_user, module, standard, app)")
    print("=" * 80)
    sidebars = frappe.get_all(
        "Workspace Sidebar",
        fields=["name", "title", "for_user", "module", "standard", "app"],
        order_by="title asc",
    )
    for s in sidebars:
        print("  ", s)

    print()
    print("=" * 80)
    print("STEP 2: full 'items' child table for each Workspace Sidebar whose module/title looks gym-related")
    print("=" * 80)
    for s in sidebars:
        title = (s.title or "")
        module = (s.module or "")
        if "gym" in title.lower() or "impact" in title.lower() or "front desk" in title.lower() or "gym" in module.lower():
            print(f"--- Workspace Sidebar: {s.name} (title={s.title}, for_user={s.for_user}, module={s.module}, standard={s.standard}) ---")
            doc = frappe.get_doc("Workspace Sidebar", s.name)
            for it in doc.items:
                print("    ", it.as_dict())
            print()

    print("=" * 80)
    print("STEP 3: does ANY Workspace Sidebar Item anywhere already link to 'Sales Invoice'?")
    print("=" * 80)
    existing = frappe.get_all(
        "Workspace Sidebar Item",
        filters={"link_to": "Sales Invoice"},
        fields=["name", "parent", "label", "type", "link_type", "link_to"],
    )
    for e in existing:
        print("  ", e)

    print()
    print("DONE.")
