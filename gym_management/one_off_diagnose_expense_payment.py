import frappe
import subprocess

def run():
    print("=" * 60)
    print("RECORD EXPENSE PAGE FILES")
    print("=" * 60)
    out = subprocess.run(["find", "/home/frappe/frappe-bench/apps/gym_management", "-iname", "*record_expense*"], capture_output=True, text=True)
    print(out.stdout)

    print()
    print("=" * 60)
    print("DOES RECORD EXPENSE PAGE SAVE INTO 'Gym Expense' DOCTYPE?")
    print("=" * 60)
    out3 = subprocess.run(["grep", "-rn", "Gym Expense", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/page/record_expense/"], capture_output=True, text=True)
    print(out3.stdout or "NOTHING FOUND — record_expense does NOT reference Gym Expense doctype directly")

    print()
    print("=" * 60)
    print("FULL record_expense.py CONTENT (backend logic)")
    print("=" * 60)
    out3b = subprocess.run(["find", "/home/frappe/frappe-bench/apps/gym_management", "-iname", "record_expense.py"], capture_output=True, text=True)
    for f in out3b.stdout.strip().split("\n"):
        if f:
            print(f"--- {f} ---")
            print(subprocess.run(["cat", f], capture_output=True, text=True).stdout)

    print()
    print("=" * 60)
    print("IS 'Gym Payment Entry' REFERENCED ANYWHERE IN THE APP CODE?")
    print("=" * 60)
    out4 = subprocess.run(["grep", "-rln", "Gym Payment Entry", "/home/frappe/frappe-bench/apps/gym_management/gym_management/"], capture_output=True, text=True)
    print(out4.stdout or "NOT REFERENCED ANYWHERE IN CODE")

    print()
    print("=" * 60)
    print("DOES SELL MEMBERSHIP BACKEND CREATE Sales Invoice / Payment Entry / Gym Payment Entry?")
    print("=" * 60)
    out5 = subprocess.run(["grep", "-rn", "Gym Payment Entry\\|Sales Invoice\\|\"Payment Entry\"", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/page/sell_membership/"], capture_output=True, text=True)
    print(out5.stdout)

    print()
    print("=" * 60)
    print("PERMISSIONS: Gym Expense")
    print("=" * 60)
    for role in ["Gym Front Desk", "Gym Manager"]:
        std = frappe.get_all("DocPerm", filters={"parent": "Gym Expense", "role": role}, fields=["read", "write", "create", "delete"])
        custom = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Expense", "role": role}, fields=["read", "write", "create", "delete"])
        print(f"{role}: standard={std} custom={custom}")

    print()
    print("=" * 60)
    print("PERMISSIONS: Gym Payment Entry")
    print("=" * 60)
    for role in ["Gym Front Desk", "Gym Manager"]:
        std = frappe.get_all("DocPerm", filters={"parent": "Gym Payment Entry", "role": role}, fields=["read", "write", "create", "delete"])
        custom = frappe.get_all("Custom DocPerm", filters={"parent": "Gym Payment Entry", "role": role}, fields=["read", "write", "create", "delete"])
        print(f"{role}: standard={std} custom={custom}")

    print()
    print("=" * 60)
    print("RECORD COUNTS (is Gym Payment Entry actually being used at all?)")
    print("=" * 60)
    print("Gym Expense records:", frappe.db.count("Gym Expense"))
    print("Gym Payment Entry records:", frappe.db.count("Gym Payment Entry"))
    print("Sales Invoice records:", frappe.db.count("Sales Invoice"))
