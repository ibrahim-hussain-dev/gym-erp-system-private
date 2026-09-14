import frappe

def run():
    keep_workspace = "Gym Operations"
    all_workspaces = frappe.get_all("Workspace", pluck="name")
    other_workspaces = [w for w in all_workspaces if w != keep_workspace]

    for wname in other_workspaces:
        try:
            frappe.db.set_value("Workspace", wname, "is_hidden", 1)
            print(f"{wname}: is_hidden = 1")
        except Exception as e:
            print(f"{wname}: SKIPPED ({e})")

    # Developer keeps ability to see hidden workspaces
    user = frappe.get_doc("User", "iibrahimhere@gmail.com")
    if not any(r.role == "Workspace Manager" for r in user.roles):
        user.append("roles", {"role": "Workspace Manager"})
        user.save(ignore_permissions=True)
        print("Added Workspace Manager role to developer account")
    else:
        print("Developer already has Workspace Manager")

    frappe.clear_cache()
    frappe.db.commit()
    print("DONE")
