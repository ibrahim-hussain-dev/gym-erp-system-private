import frappe


def run():
    print("=== Enabled users and their roles (excluding Administrator/Guest) ===")
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
        fields=["name", "full_name", "user_type"],
    )
    for u in users:
        roles = frappe.get_roles(u["name"])
        print(f"  {u['name']} (full_name={u['full_name']!r}, user_type={u['user_type']!r})")
        print(f"    roles: {roles}")
        print()

    print("=== Administrator roles (for reference / escape-hatch check) ===")
    print(f"  Administrator roles: {frappe.get_roles('Administrator')}")
