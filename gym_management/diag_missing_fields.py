import frappe


def run():
    print("=" * 80)
    print("STEP 1: Gym Fitness Log - 'height_cm' field/column check")
    print("=" * 80)
    meta = frappe.get_meta("Gym Fitness Log")
    has_field = any(f.fieldname == "height_cm" for f in meta.fields)
    print(f"  'height_cm' defined in Gym Fitness Log doctype: {has_field}")
    cols = frappe.db.sql("SHOW COLUMNS FROM `tabGym Fitness Log`", as_dict=True)
    col_names = [c.Field for c in cols]
    print(f"  'height_cm' exists as DB column: {'height_cm' in col_names}")
    print("  Existing fields (fieldname: fieldtype), in order:")
    for f in meta.fields:
        print(f"    {f.fieldname}: {f.fieldtype}")

    print()
    print("=" * 80)
    print("STEP 2: Gym Subscription - 'auto_renew' field/column check")
    print("=" * 80)
    meta2 = frappe.get_meta("Gym Subscription")
    has_field2 = any(f.fieldname == "auto_renew" for f in meta2.fields)
    print(f"  'auto_renew' defined in Gym Subscription doctype: {has_field2}")
    cols2 = frappe.db.sql("SHOW COLUMNS FROM `tabGym Subscription`", as_dict=True)
    col_names2 = [c.Field for c in cols2]
    print(f"  'auto_renew' exists as DB column: {'auto_renew' in col_names2}")
    print("  Existing fields (fieldname: fieldtype), in order:")
    for f in meta2.fields:
        print(f"    {f.fieldname}: {f.fieldtype}")

    print()
    print("DONE.")
