import frappe

def run():
    reports = [
        {"report_name": "Gym Trainer Commission", "ref_doctype": "Gym Trainer"},
        {"report_name": "Gym Revenue by Plan", "ref_doctype": "Sales Invoice"},
        {"report_name": "Gym Membership Retention", "ref_doctype": "Gym Subscription"},
    ]
    for r in reports:
        if frappe.db.exists("Report", r["report_name"]):
            print(f"Already exists: {r['report_name']}")
            continue
        doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": r["report_name"],
            "ref_doctype": r["ref_doctype"],
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Gym-ERP-System",
            "disabled": 0,
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        print(f"Created report: {doc.name}")
    frappe.db.commit()
