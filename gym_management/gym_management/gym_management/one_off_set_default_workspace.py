import frappe

def run():
    target_roles = ["Gym Front Desk", "Gym Trainer", "Gym Manager"]
    updated = []
    for role in target_roles:
        users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
        for u in set(users):
            if u in ("Administrator", "Guest"):
                continue
            frappe.db.set_value("User", u, "default_workspace", "Gym Operations")
            updated.append((u, role))
    frappe.db.commit()
    print("Updated users:", updated)
