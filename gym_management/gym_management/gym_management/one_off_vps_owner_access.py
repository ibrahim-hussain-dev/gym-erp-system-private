import frappe

def run():
    user_email = "iibrahimhere@gmail.com"
    user = frappe.get_doc("User", user_email)
    keep_roles = {"System Manager", "Gym Manager"}
    user.roles = [r for r in user.roles if r.role in keep_roles]
    existing = {r.role for r in user.roles}
    for role in keep_roles:
        if role not in existing:
            user.append("roles", {"role": role})
    user.save(ignore_permissions=True)
    frappe.db.commit()
    print("Final roles for", user_email, ":", [r.role for r in user.roles])
    print("DONE")
