import frappe

def run():
    if frappe.db.exists("Client Script", "Gym Member"):
        frappe.delete_doc("Client Script", "Gym Member", force=True, ignore_permissions=True)
        frappe.db.commit()
        print("Deleted broken legacy Client Script: Gym Member")
    else:
        print("Not found, nothing to delete.")
