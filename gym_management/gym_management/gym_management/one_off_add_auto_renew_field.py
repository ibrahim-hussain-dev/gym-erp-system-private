import frappe

def run():
    if not frappe.db.exists("Custom Field", {"dt": "Gym Subscription", "fieldname": "auto_renew"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Gym Subscription",
            "fieldname": "auto_renew",
            "label": "Auto Renew",
            "fieldtype": "Check",
            "insert_after": "status",
            "default": "0",
            "description": "If checked, this membership will be automatically renewed (new invoice + new subscription) when it expires.",
        }).insert(ignore_permissions=True)
        print("Added auto_renew field to Gym Subscription.")
    else:
        print("auto_renew field already exists, skipping.")
    frappe.db.commit()
