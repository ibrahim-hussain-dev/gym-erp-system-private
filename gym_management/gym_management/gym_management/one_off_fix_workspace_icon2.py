import frappe

def run():
    ws = frappe.get_doc("Workspace", "Gym Operations")
    ws.icon = "activity"
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("Icon set to 'activity'")
