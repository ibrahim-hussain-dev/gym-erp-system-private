import frappe


def run():
    old = frappe.db.get_single_value("System Settings", "session_expiry")
    frappe.db.set_single_value("System Settings", "session_expiry", "08:00")
    frappe.clear_cache()
    frappe.db.commit()
    new = frappe.db.get_single_value("System Settings", "session_expiry")
    print(f"session_expiry changed: {old!r} -> {new!r}")
