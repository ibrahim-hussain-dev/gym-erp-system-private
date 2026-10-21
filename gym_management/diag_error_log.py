import frappe


def run():
    print("=" * 80)
    print("STEP 1: recent Error Log entries (last 20) mentioning Impact Health Studio / height_cm / Front Desk / Workspace")
    print("=" * 80)
    logs = frappe.get_all(
        "Error Log",
        filters={},
        fields=["name", "creation", "method", "error"],
        order_by="creation desc",
        limit=40,
    )
    keywords = ["height_cm", "impact-health-studio", "Impact Health Studio", "Front Desk", "Workspace", "workspace", "Number Card"]
    shown = 0
    for l in logs:
        text = (l.error or "") + " " + (l.method or "")
        if any(k in text for k in keywords):
            print(f"--- {l.creation} | {l.method} ---")
            print((l.error or "")[:1500])
            print()
            shown += 1
        if shown >= 8:
            break
    if shown == 0:
        print("  no matching recent error log entries found; printing latest 5 regardless")
        for l in logs[:5]:
            print(f"--- {l.creation} | {l.method} ---")
            print((l.error or "")[:1000])
            print()

    print()
    print("=" * 80)
    print("STEP 2: does 'Gym Member' doctype JSON define 'height_cm' and does the DB column exist?")
    print("=" * 80)
    meta = frappe.get_meta("Gym Member")
    has_field = any(f.fieldname == "height_cm" for f in meta.fields)
    print(f"  'height_cm' defined in Gym Member doctype: {has_field}")
    cols = frappe.db.sql("SHOW COLUMNS FROM `tabGym Member`", as_dict=True)
    col_names = [c.Field for c in cols]
    print(f"  'height_cm' exists as actual DB column: {'height_cm' in col_names}")

    print()
    print("DONE.")
