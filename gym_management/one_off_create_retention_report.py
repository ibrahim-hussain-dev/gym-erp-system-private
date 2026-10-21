import frappe

def run():
    if frappe.db.exists("Report", "Gym Member Retention"):
        print("Already exists")
        return
    frappe.get_doc({
        "doctype": "Report",
        "report_name": "Gym Member Retention",
        "ref_doctype": "Gym Subscription",
        "report_type": "Script Report",
        "is_standard": "Yes",
        "module": "Gym-ERP-System",
        "roles": [{"role": "Gym Manager"}]
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Created Report: Gym Member Retention")
