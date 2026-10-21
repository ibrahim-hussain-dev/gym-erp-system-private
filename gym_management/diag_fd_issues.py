import frappe


def run():
    print("=" * 80)
    print("STEP 1: Custom DocPerm + meta permissions for 'Gym Trainer' (Gym Front Desk / Gym Owner)")
    print("=" * 80)
    dt = "Gym Trainer"
    rows = frappe.get_all(
        "Custom DocPerm",
        filters={"parent": dt},
        fields=["role", "permlevel", "read", "write", "create", "submit", "cancel", "if_owner"],
        order_by="role asc",
    )
    print(f"  Custom DocPerm rows for '{dt}' ({len(rows)}):")
    for r in rows:
        print("    ", r)
    meta = frappe.get_meta(dt)
    print(f"  meta.permissions for '{dt}' (Gym roles only):")
    for p in meta.permissions:
        if p.role in ("Gym Owner", "Gym Front Desk"):
            print("    ", p.as_dict())

    print()
    print("=" * 80)
    print("STEP 2: Custom DocPerm for 'Gym Expense' (backing doctype for Record Expense page)")
    print("=" * 80)
    dt2 = "Gym Expense"
    rows2 = frappe.get_all(
        "Custom DocPerm",
        filters={"parent": dt2},
        fields=["role", "permlevel", "read", "write", "create", "submit", "cancel", "if_owner"],
        order_by="role asc",
    )
    print(f"  Custom DocPerm rows for '{dt2}' ({len(rows2)}):")
    for r in rows2:
        print("    ", r)

    print()
    print("=" * 80)
    print("STEP 3: Re-check Website Settings / Navbar Settings app_logo + backing File record")
    print("=" * 80)
    ws_logo = frappe.db.get_value("Website Settings", "Website Settings", "app_logo")
    nb_logo = frappe.db.get_value("Navbar Settings", "Navbar Settings", "app_logo")
    print(f"  Website Settings.app_logo = {ws_logo}")
    print(f"  Navbar Settings.app_logo = {nb_logo}")
    for path in [ws_logo, nb_logo]:
        if path:
            f = frappe.db.get_value(
                "File", {"file_url": path}, ["name", "is_private", "file_url", "attached_to_doctype", "attached_to_name"], as_dict=True
            )
            print(f"    File record for {path}: {f}")

    print()
    print("=" * 80)
    print("STEP 4: Front Desk role - Has Role entries on the 3 custom Pages")
    print("=" * 80)
    for pg in ["sell-membership", "mark-attendance", "record-expense"]:
        if frappe.db.exists("Page", pg):
            roles = frappe.get_all("Has Role", filters={"parent": pg, "parenttype": "Page"}, fields=["role"])
            print(f"  Page '{pg}': roles = {[r.role for r in roles]}")

    print()
    print("DONE.")
