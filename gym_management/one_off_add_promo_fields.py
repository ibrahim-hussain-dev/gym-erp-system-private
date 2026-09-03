import frappe

def run():
    if not frappe.db.exists("Custom Field", {"dt": "Gym Promo Code", "fieldname": "times_used"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Gym Promo Code",
            "fieldname": "times_used",
            "label": "Times Used",
            "fieldtype": "Int",
            "insert_after": "single_use_per_member",
            "read_only": 1,
            "default": "0",
        }).insert(ignore_permissions=True)
        print("Added times_used to Gym Promo Code.")
    else:
        print("times_used already exists, skipping.")

    if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "promo_code"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Sales Invoice",
            "fieldname": "promo_code",
            "label": "Promo Code Used",
            "fieldtype": "Data",
            "insert_after": "gym_member",
            "read_only": 1,
        }).insert(ignore_permissions=True)
        print("Added promo_code to Sales Invoice.")
    else:
        print("promo_code already exists, skipping.")

    frappe.db.commit()
