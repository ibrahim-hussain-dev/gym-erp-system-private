import frappe

def run():
    for role in ["Gym Front Desk", "Gym Manager"]:
        existing = frappe.db.exists("Custom DocPerm", {"parent": "Mode of Payment", "role": role, "permlevel": 0})
        if existing:
            frappe.delete_doc("Custom DocPerm", existing, force=True, ignore_permissions=True)
        doc = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": "Mode of Payment",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": 0,
            "read": 1
        })
        doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Mode of Payment read access granted to Gym Front Desk aur Gym Manager")
