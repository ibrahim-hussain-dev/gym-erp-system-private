import frappe
import subprocess


def run():
    print("=" * 70)
    print("STEP 0: grep for price_per_session across gym_management app")
    print("=" * 70)
    try:
        out = subprocess.run(
            ["grep", "-rn", "price_per_session", "/home/frappe/frappe-bench/apps/gym_management/gym_management/"],
            capture_output=True, text=True,
        )
        print(out.stdout or "(no matches)")
        if out.stderr:
            print("grep stderr:", out.stderr)
    except Exception as e:
        print("grep failed:", e)

    dt = "Gym Trainer"

    print("=" * 70)
    print("STEP 1: remove the field from Gym Trainer (native or Custom Field)")
    print("=" * 70)

    original_dev_mode = frappe.conf.get("developer_mode")
    frappe.conf.developer_mode = 1
    try:
        doc = frappe.get_doc("DocType", dt)
        before = len(doc.fields)
        target_fieldnames = set()
        for f in doc.fields:
            if f.fieldname == "price_per_session" or (f.label or "").strip().lower() == "price per session":
                target_fieldnames.add(f.fieldname)
        if target_fieldnames:
            doc.fields = [f for f in doc.fields if f.fieldname not in target_fieldnames]
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"Removed native field(s) {target_fieldnames} from {dt}. Fields {before} -> {len(doc.fields)}")
        else:
            print(f"No native field named 'price_per_session' / labeled 'Price Per Session' found on {dt}.")
    finally:
        frappe.conf.developer_mode = original_dev_mode

    cf_list = frappe.get_all("Custom Field", filters={"dt": dt}, fields=["name", "fieldname", "label"])
    for cf in cf_list:
        if cf.fieldname == "price_per_session" or (cf.label or "").strip().lower() == "price per session":
            frappe.delete_doc("Custom Field", cf.name, ignore_permissions=True)
            frappe.db.commit()
            print(f"Deleted Custom Field {cf.name} ({cf.fieldname}) from {dt}.")

    frappe.clear_cache(doctype=dt)

    print("=" * 70)
    print("STEP 2: sanity check")
    print("=" * 70)
    print("Gym Trainer has 'price_per_session' field now:", frappe.get_meta(dt).has_field("price_per_session"))
    print("DONE.")
