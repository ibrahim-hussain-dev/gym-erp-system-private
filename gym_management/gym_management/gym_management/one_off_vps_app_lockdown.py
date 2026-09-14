import frappe

def run():
    # 1. Diagnostic: check what our own default-workspace hook does
    try:
        import gym_management.gym_erp_system.user_setup as us
        import inspect
        print("=== user_setup.py source ===")
        print(inspect.getsource(us))
    except Exception as e:
        print("Could not load user_setup module:", e)

    # 2. Remove System Manager from the owner account - Gym Manager only
    user_email = "iibrahimhere@gmail.com"
    user = frappe.get_doc("User", user_email)
    user.roles = [r for r in user.roles if r.role == "Gym Manager"]
    if not any(r.role == "Gym Manager" for r in user.roles):
        user.append("roles", {"role": "Gym Manager"})
    user.save(ignore_permissions=True)
    print("Roles now:", [r.role for r in user.roles])

    # 3. Set Role Home Page so login lands directly on Gym Operations workspace
    for role in ["Gym Manager", "Gym Front Desk", "Gym Trainer"]:
        if not frappe.db.exists("Role Home Page", {"role": role}):
            frappe.get_doc({
                "doctype": "Role Home Page",
                "role": role,
                "home_page": "/app/gym-operations",
            }).insert(ignore_permissions=True)
            print("Set home page for role:", role)
        else:
            frappe.db.set_value("Role Home Page", {"role": role}, "home_page", "/app/gym-operations")
            print("Updated home page for role:", role)

    frappe.db.commit()
    print("DONE")
