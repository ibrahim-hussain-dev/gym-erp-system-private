import frappe


def run():
    leftover = frappe.get_all("User", filters={"email": ["like", "rbac.%test%"]}, fields=["name", "email"])
    leftover += frappe.get_all("User", filters={"email": ["like", "rbac.%diag%"]}, fields=["name", "email"])
    if leftover:
        print("LEFTOVER TEST USERS FOUND:")
        for u in leftover:
            print(" ", u.email)
    else:
        print("CLEAN - no leftover test users found.")
