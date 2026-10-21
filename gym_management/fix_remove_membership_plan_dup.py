import frappe


def run():
    print("=" * 80)
    print("STEP 1: remove the duplicate 'Membership Plan' sidebar item")
    print("        (it links to the same DocType as 'Gym Plan')")
    print("=" * 80)

    sidebar_names = frappe.get_all("Workspace Sidebar", pluck="name")
    print(f"  found {len(sidebar_names)} Workspace Sidebar doc(s): {sidebar_names}")

    total_removed = 0
    for name in sidebar_names:
        ws = frappe.get_doc("Workspace Sidebar", name)
        before = len(ws.items)
        kept = []
        removed_here = []
        for it in ws.items:
            if it.link_type == "DocType" and it.link_to == "Gym Plan" and it.label == "Membership Plan":
                removed_here.append(it.label)
                total_removed += 1
                continue
            kept.append(it)
        if removed_here:
            ws.items = kept
            for idx, it in enumerate(ws.items, start=1):
                it.idx = idx
            ws.save(ignore_permissions=True)
            print(f"  [{name}] before={before} after={len(ws.items)} removed={removed_here}")
        else:
            print(f"  [{name}] no matching items found, left untouched ({before} items)")

    print()
    print(f"  total items removed across all sidebars: {total_removed}")
    if total_removed == 0:
        frappe.throw("Expected to remove at least one 'Membership Plan' item, removed none")

    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("=" * 80)
    print("STEP 2: verify")
    print("=" * 80)
    for name in sidebar_names:
        ws = frappe.get_doc("Workspace Sidebar", name)
        remaining_flagged = [
            it.label for it in ws.items
            if it.link_type == "DocType" and it.link_to == "Gym Plan" and it.label == "Membership Plan"
        ]
        gym_plan_labels = [it.label for it in ws.items if it.link_type == "DocType" and it.link_to == "Gym Plan"]
        print(f"  [{name}] total items now: {len(ws.items)}, remaining 'Gym Plan' links: {gym_plan_labels}")

    print()
    print("DONE.")
