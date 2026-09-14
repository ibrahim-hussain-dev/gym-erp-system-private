import frappe

def run():
    print("=== Gym Operations workspace ===")
    gw = frappe.get_doc("Workspace", "Gym Operations")
    print("public:", gw.public, "| is_hidden:", gw.is_hidden, "| roles:", [r.role for r in gw.roles])

    print("\n=== Home workspace ===")
    hw = frappe.get_doc("Workspace", "Home")
    print("public:", hw.public, "| is_hidden:", hw.is_hidden, "| roles:", [r.role for r in hw.roles])

    print("\n=== default_workspace per user ===")
    for e in ["iibrahimhere@gmail.com", "owner@gym.local", "fd1@gym.local"]:
        print(e, "->", frappe.db.get_value("User", e, "default_workspace"))

    print("\n=== actual roles per user ===")
    for e in ["iibrahimhere@gmail.com", "owner@gym.local", "fd1@gym.local"]:
        roles = [r.role for r in frappe.get_doc("User", e).roles]
        print(e, "->", roles)
