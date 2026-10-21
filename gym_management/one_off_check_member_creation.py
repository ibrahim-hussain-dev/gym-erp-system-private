import frappe
import subprocess

def run():
    print("=" * 60)
    print("DOES SELL MEMBERSHIP SUPPORT CREATING A BRAND-NEW MEMBER?")
    print("=" * 60)
    out = subprocess.run(["grep", "-n", "-B2", "-A6", "Gym Member", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/page/sell_membership/sell_membership.js"], capture_output=True, text=True)
    print(out.stdout)

    print()
    print("=" * 60)
    print("CURRENT PERMISSIONS: Gym Member")
    print("=" * 60)
    for role in ["Gym Front Desk", "Gym Manager"]:
        std = frappe.get_all("DocPerm", filters={"parent": "Gym Member", "role": role}, fields=["read", "write", "create", "delete"])
        custom = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Member", "role": role}, fields=["read", "write", "create", "delete"])
        print(f"{role}: standard={std} custom={custom}")

    print()
    print("=" * 60)
    print("APPLYING: remove 'create' on Gym Expense for Gym Manager (safe, low-risk fix)")
    print("=" * 60)
    existing = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Expense", "role": "Gym Manager", "permlevel": 0})
    for e in existing:
        frappe.db.set_value("Custom DocPerm", e.name, "create", 0)
    print("Gym Manager -> Gym Expense: create=0 (read/write untouched)")
    frappe.db.commit()
    print("DONE")
