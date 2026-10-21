import frappe


def run():
    print("=" * 80)
    print("STEP 1: module field for Payment Entry vs Sales Invoice (the key comparison)")
    print("=" * 80)
    for dt in ["Payment Entry", "Sales Invoice", "Gym Plan", "Gym Promo Code", "Gym Fitness Log"]:
        m = frappe.db.get_value("DocType", dt, "module")
        print(f"  {dt}: module = {m}")

    print()
    print("=" * 80)
    print("STEP 2: ALL DocTypes with module = 'Gym-ERP-System'")
    print("=" * 80)
    dts = frappe.get_all("DocType", filters={"module": "Gym-ERP-System"}, fields=["name"])
    print("  ", [d.name for d in dts])

    print()
    print("=" * 80)
    print("STEP 3: ALL Report docs with module = 'Gym-ERP-System'")
    print("=" * 80)
    reports = frappe.get_all("Report", filters={"module": "Gym-ERP-System"}, fields=["name", "report_type"])
    print("  ", reports)

    print()
    print("DONE.")
