import frappe

def run():
    fields = [
        {
            "dt": "Gym Trainer",
            "fieldname": "sessions_attended",
            "label": "Sessions Attended",
            "fieldtype": "Int",
            "insert_after": "price_per_session",
            "read_only": 1,
        },
        {
            "dt": "Gym Trainer",
            "fieldname": "total_commission",
            "label": "Total Commission",
            "fieldtype": "Currency",
            "insert_after": "sessions_attended",
            "read_only": 1,
        },
    ]
    for f in fields:
        if frappe.db.exists("Custom Field", {"dt": f["dt"], "fieldname": f["fieldname"]}):
            continue
        frappe.get_doc({"doctype": "Custom Field", **f}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Added sessions_attended and total_commission fields to Gym Trainer.")
