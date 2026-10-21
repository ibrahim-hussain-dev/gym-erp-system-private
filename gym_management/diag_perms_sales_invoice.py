import frappe


def run():
    print("=" * 80)
    print("STEP 1: Custom DocPerm rows for Sales Invoice vs Payment Entry")
    print("=" * 80)
    for dt in ["Sales Invoice", "Payment Entry"]:
        rows = frappe.get_all(
            "Custom DocPerm",
            filters={"parent": dt},
            fields=["name", "role", "permlevel", "read", "write", "create", "submit", "cancel", "amend", "if_owner"],
            order_by="role asc, permlevel asc",
        )
        print(f"  Custom DocPerm for '{dt}' ({len(rows)} rows):")
        for r in rows:
            print("    ", r)
        print()

    print("=" * 80)
    print("STEP 2: Standard permissions defined in the doctype's own meta, filtered to relevant roles")
    print("=" * 80)
    for dt in ["Sales Invoice", "Payment Entry"]:
        meta = frappe.get_meta(dt)
        print(f"  Standard permissions on '{dt}' meta.permissions (Gym/All/System Manager roles only):")
        for p in meta.permissions:
            if p.role in ("Gym Owner", "Gym Front Desk", "All", "System Manager"):
                print("    ", p.as_dict())
        print()

    print("=" * 80)
    print("STEP 3: Does Gym Owner / Gym Front Desk have any Custom DocPerm row at all on these doctypes?")
    print("=" * 80)
    for dt in ["Sales Invoice", "Payment Entry"]:
        for role in ["Gym Owner", "Gym Front Desk"]:
            rows = frappe.get_all(
                "Custom DocPerm",
                filters={"parent": dt, "role": role},
                fields=["permlevel", "read", "write", "if_owner"],
            )
            print(f"  {dt} / role={role}: {rows if rows else 'NO CUSTOM DOCPERM ROW FOR THIS ROLE'}")

    print()
    print("DONE.")
