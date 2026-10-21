import frappe

def run():
    if frappe.db.exists("Page", "manage-subscription"):
        print("Page already exists, skipping.")
        return
    frappe.get_doc({
        "doctype": "Page",
        "name": "manage-subscription",
        "page_name": "manage-subscription",
        "title": "Freeze / Resume Membership",
        "module": "Gym-ERP-System",
        "standard": "Yes",
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Created Page: manage-subscription")
