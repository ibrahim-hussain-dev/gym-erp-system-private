import frappe

def run():
    print("session_expiry:", frappe.db.get_single_value("System Settings", "session_expiry"))
