import frappe

def run():
    keep_workspace = "Gym Operations"
    all_workspaces = frappe.get_all("Workspace", pluck="name")
    other_workspaces = [w for w in all_workspaces if w != keep_workspace]
    print("Other workspaces found:", other_workspaces)

    for wname in other_workspaces:
        try:
            ws = frappe.get_doc("Workspace", wname)
            ws.set("roles", [])
            ws.append("roles", {"role": "System Manager"})
            ws.flags.ignore_mandatory = True
            ws.flags.ignore_validate = True
            ws.save(ignore_permissions=True)
            print(f"{wname}: OK -> restricted to System Manager")
        except Exception as e:
            print(f"{wname}: SKIPPED (error: {e})")

    user_meta = frappe.get_meta("User")
    has_default_workspace = any(f.fieldname == "default_workspace" for f in user_meta.fields)
    print("User.default_workspace field exists:", has_default_workspace)

    for email in ["iibrahimhere@gmail.com", "owner@gym.local", "fd1@gym.local"]:
        if not frappe.db.exists("User", email):
            continue
        if has_default_workspace:
            frappe.db.set_value("User", email, "default_workspace", "Gym Operations")
            print(email, "-> default_workspace set to Gym Operations")

    for role in ["Gym Owner", "Gym Front Desk", "Gym Trainer"]:
        if frappe.db.exists("Role Home Page", {"role": role}):
            frappe.db.set_value("Role Home Page", {"role": role}, "home_page", "/app/gym-operations")
        else:
            frappe.get_doc({"doctype": "Role Home Page", "role": role, "home_page": "/app/gym-operations"}).insert(ignore_permissions=True)
        print(role, "-> role home page set to /app/gym-operations")

    for email in ["iibrahimhere@gmail.com", "owner@gym.local", "fd1@gym.local"]:
        frappe.clear_cache(user=email)
    frappe.clear_cache()
    frappe.db.commit()
    print("DONE")
