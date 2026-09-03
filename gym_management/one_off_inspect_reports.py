import frappe

def run():
    for report_name in ["Gym Master Report", "Gym Monthly Income"]:
        if not frappe.db.exists("Report", report_name):
            print(f"=== {report_name}: NOT FOUND as a Report doctype ===")
            continue
        r = frappe.get_doc("Report", report_name)
        print(f"=== {report_name} ===")
        print("report_type:", r.report_type)
        print("ref_doctype:", r.ref_doctype)
        print("filters json:")
        print(r.json)
        print()
