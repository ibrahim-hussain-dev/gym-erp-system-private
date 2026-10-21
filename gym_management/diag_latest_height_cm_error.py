import frappe


def run():
    print("=" * 80)
    print("STEP 1: latest 3 Error Log entries mentioning 'height_cm', FULL traceback")
    print("=" * 80)
    logs = frappe.get_all(
        "Error Log",
        filters={},
        fields=["name", "creation", "method", "error"],
        order_by="creation desc",
        limit=100,
    )
    shown = 0
    for l in logs:
        if "height_cm" in (l.error or ""):
            print(f"--- {l.name} | {l.creation} | method={l.method} ---")
            print(l.error or "")
            print()
            print("-" * 80)
            print()
            shown += 1
        if shown >= 3:
            break
    if shown == 0:
        print("  no Error Log entries mention 'height_cm' in the last 100 entries")

    print()
    print("=" * 80)
    print("STEP 2: re-confirm Gym Fitness Log meta + DB columns right now")
    print("=" * 80)
    meta = frappe.get_meta("Gym Fitness Log")
    has_field = any(f.fieldname == "height_cm" for f in meta.fields)
    print(f"  'height_cm' defined in Gym Fitness Log doctype (fresh meta): {has_field}")
    cols = frappe.db.sql("SHOW COLUMNS FROM `tabGym Fitness Log`", as_dict=True)
    col_names = [c.Field for c in cols]
    print(f"  'height_cm' exists as DB column (fresh query): {'height_cm' in col_names}")

    print()
    print("=" * 80)
    print("STEP 3: which SITE / DB is this bench process actually using")
    print("=" * 80)
    print(f"  frappe.local.site = {frappe.local.site}")
    print(f"  db name = {frappe.conf.db_name}")
    print(f"  db host = {frappe.conf.get('db_host')}")

    print()
    print("DONE.")
