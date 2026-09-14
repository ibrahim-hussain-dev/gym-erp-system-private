import frappe

def run():
    user_email = "iibrahimhere@gmail.com"
    user = frappe.get_doc("User", user_email)
    print("Current default_workspace:", user.default_workspace)

    ws = frappe.get_doc("Workspace", "Gym Operations")
    print("Gym Operations workspace - public:", ws.public, "| module:", ws.module)

    user.db_set("default_workspace", "Gym Operations", update_modified=False)
    frappe.db.commit()

    user.reload()
    print("New default_workspace:", user.default_workspace)
    print("DONE")
