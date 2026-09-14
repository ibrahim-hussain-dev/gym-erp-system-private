import frappe

def run():
    target_roles = ["Gym Front Desk", "Gym Trainer", "Gym Manager"]
    print("=== Gym-role users aur unka default_workspace ===")
    seen = set()
    for role in target_roles:
        users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
        for u in set(users):
            if u == "Administrator" or u in seen:
                continue
            seen.add(u)
            dw = frappe.db.get_value("User", u, "default_workspace")
            enabled = frappe.db.get_value("User", u, "enabled")
            print(f"{u} | role={role} | default_workspace={dw} | enabled={enabled}")
    if not seen:
        print("KOI GYM-ROLE USER NAHI MILA - abhi tak sirf Administrator hi hai")
