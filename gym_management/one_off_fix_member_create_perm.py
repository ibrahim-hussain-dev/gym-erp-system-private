import frappe

def run():
    for role in ["Gym Front Desk", "Gym Manager"]:
        existing = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Member", "role": role, "permlevel": 0})
        for e in existing:
            frappe.db.set_value("Custom DocPerm", e.name, "create", 0)
        print(f"{role} -> Gym Member: create=0 (read/write untouched)")
    frappe.db.commit()
    print("DONE")
