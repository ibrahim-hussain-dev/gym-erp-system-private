import json

import frappe


def run():
    print("=" * 80)
    print("STEP 1: remove 'Promo Codes' item from Impact Health Studio Workspace Sidebar")
    print("=" * 80)
    ws = frappe.get_doc("Workspace Sidebar", "Impact Health Studio")
    before = len(ws.items)
    ws.items = [
        it for it in ws.items
        if not (it.label == "Promo Codes" and it.link_to == "Gym Promo Code")
    ]
    after = len(ws.items)
    removed_items = before - after
    print(f"  items before: {before}, after: {after}, removed: {removed_items}")
    if removed_items != 1:
        frappe.throw(f"Expected to remove exactly 1 sidebar item, removed {removed_items}")
    for idx, it in enumerate(ws.items, start=1):
        it.idx = idx
    ws.save(ignore_permissions=True)

    print()
    print("=" * 80)
    print("STEP 2: delete Custom DocPerm rows for Gym Promo Code (safety net)")
    print("=" * 80)
    perm_rows = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Promo Code"}, pluck="name")
    print(f"  found {len(perm_rows)} Custom DocPerm row(s): {perm_rows}")
    for r in perm_rows:
        frappe.delete_doc("Custom DocPerm", r, force=True, ignore_permissions=True)
    print("  deleted.")

    print()
    print("=" * 80)
    print("STEP 3: delete the 'Gym Promo Code' DocType (drops its table + the 1 existing record)")
    print("=" * 80)
    if frappe.db.exists("DocType", "Gym Promo Code"):
        frappe.delete_doc("DocType", "Gym Promo Code", force=True, ignore_permissions=True)
        print("  Deleted DocType 'Gym Promo Code'.")
    else:
        print("  DocType 'Gym Promo Code' does not exist, nothing to delete.")

    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("=" * 80)
    print("STEP 4: verify")
    print("=" * 80)
    print("  DocType 'Gym Promo Code' exists:", frappe.db.exists("DocType", "Gym Promo Code"))
    print("  Table 'tabGym Promo Code' exists:", frappe.db.table_exists("Gym Promo Code"))
    remaining_perms = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Promo Code"})
    print("  remaining Custom DocPerm rows for Gym Promo Code:", len(remaining_perms))
    ws2 = frappe.get_doc("Workspace Sidebar", "Impact Health Studio")
    promo_items = [it.label for it in ws2.items if "promo" in (it.label or "").lower()]
    print("  remaining sidebar items mentioning promo:", promo_items)
    print("  total sidebar items now:", len(ws2.items))

    print()
    print("DONE.")
