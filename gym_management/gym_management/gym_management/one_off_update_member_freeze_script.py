import frappe

def run():
    with open("/tmp/gym_member_freeze.js") as f:
        new_script = f.read()

    existing = frappe.get_all("Client Script", filters={"dt": "Gym Member"}, fields=["name"])
    if existing:
        for e in existing:
            frappe.db.set_value("Client Script", e.name, "script", new_script)
            frappe.db.set_value("Client Script", e.name, "enabled", 1)
            print(f"Updated Client Script: {e.name}")
    else:
        frappe.get_doc({
            "doctype": "Client Script", "dt": "Gym Member", "view": "Form",
            "enabled": 1, "script": new_script
        }).insert(ignore_permissions=True)
        print("Created new Client Script")

    frappe.db.commit()
