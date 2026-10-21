import frappe

def run():
    email = "frontdesk.test@example.com"
    if frappe.db.exists("User", email):
        frappe.delete_doc("User", email, force=True, ignore_permissions=True)
        frappe.db.commit()

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": "Front Desk Test",
        "send_welcome_email": 0,
        "roles": [{"role": "Gym Front Desk"}]
    })
    user.insert(ignore_permissions=True)
    user.new_password = "TestPass@123"
    user.save(ignore_permissions=True)
    frappe.db.commit()

    dw = frappe.db.get_value("User", email, "default_workspace")
    print("Created user:", email)
    print("Password: TestPass@123")
    print("default_workspace set to:", dw)
