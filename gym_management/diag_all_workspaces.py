import frappe


def run():
    print("=" * 80)
    print("STEP 1: ALL Workspace records site-wide (name, label, parent_page, public, is_hidden, module)")
    print("=" * 80)
    all_ws = frappe.get_all(
        "Workspace",
        fields=["name", "label", "title", "parent_page", "public", "is_hidden", "module", "sequence_id"],
        order_by="parent_page asc, sequence_id asc",
    )
    for w in all_ws:
        print("  ", w)

    print()
    print("=" * 80)
    print("STEP 2: Workspace records with parent_page = 'Impact Health Studio'")
    print("=" * 80)
    children1 = frappe.get_all(
        "Workspace",
        filters={"parent_page": "Impact Health Studio"},
        fields=["name", "label", "title", "public", "is_hidden", "sequence_id"],
        order_by="sequence_id asc",
    )
    for c in children1:
        print("  ", c)

    print()
    print("=" * 80)
    print("STEP 3: Workspace records with parent_page = 'Front Desk'")
    print("=" * 80)
    children2 = frappe.get_all(
        "Workspace",
        filters={"parent_page": "Front Desk"},
        fields=["name", "label", "title", "public", "is_hidden", "sequence_id"],
        order_by="sequence_id asc",
    )
    for c in children2:
        print("  ", c)

    print()
    print("=" * 80)
    print("STEP 4: is there a Workspace record literally named/labelled 'Payment Entry' or 'Sales Invoice'?")
    print("=" * 80)
    for name in ["Payment Entry", "Sales Invoice"]:
        exists = frappe.db.exists("Workspace", name)
        print(f"  Workspace('{name}') exists by name: {exists}")
        by_label = frappe.get_all("Workspace", filters={"label": name}, fields=["name", "parent_page", "public", "is_hidden"])
        print(f"  Workspace by label='{name}':", by_label)

    print()
    print("DONE.")
