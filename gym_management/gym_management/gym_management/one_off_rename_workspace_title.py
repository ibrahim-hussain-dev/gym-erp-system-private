import frappe

def run():
    frappe.db.set_value("Workspace", "Gym Operations", "label", "Impact Health Studio")
    frappe.db.set_value("Workspace", "Gym Operations", "title", "Impact Health Studio")
    frappe.db.commit()
    frappe.clear_cache()
    print("Display title updated to 'Impact Health Studio' (internal route/name unchanged: Gym Operations)")
