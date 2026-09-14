import frappe

def run():
    print("=== Gym Plan docs with plan_group = Locker ===")
    rows = frappe.get_all("Gym Plan", filters={"plan_group": "Locker"}, fields=["name", "plan_name", "disabled"])
    for r in rows:
        print(r)
    if not rows:
        print("(none)")
