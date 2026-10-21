import frappe

def run():
    with open("/tmp/gym_member_manage.js") as f:
        new_script = f.read()
    existing = frappe.get_all("Client Script", filters={"dt": "Gym Member"}, fields=["name"])
    for e in existing:
        frappe.db.set_value("Client Script", e.name, "script", new_script)
        frappe.db.set_value("Client Script", e.name, "enabled", 1)
        print(f"Updated: {e.name}")
    frappe.db.commit()
