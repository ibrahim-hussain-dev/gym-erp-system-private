import frappe
import subprocess

def run():
    names_to_check = ["Gym Membership Retention", "Gym membership retention"]
    found = False
    for n in names_to_check:
        if frappe.db.exists("Report", n):
            frappe.delete_doc("Report", n, ignore_permissions=True, force=True)
            print(f"Deleted Report: {n}")
            found = True

    if not found:
        similar = frappe.get_all("Report", filters={"report_name": ["like", "%Retention%"]}, fields=["name"])
        print("All retention-like reports found:", similar)
        for s in similar:
            if s.name != "Gym Member Retention":
                frappe.delete_doc("Report", s.name, ignore_permissions=True, force=True)
                print(f"Deleted: {s.name}")

    frappe.db.commit()

    result = subprocess.run([
        "mv",
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/report/gym_membership_retention",
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/report/_deprecated_gym_membership_retention"
    ], capture_output=True, text=True)
    print("Folder move result:", result.returncode == 0, result.stderr or "(already auto-deleted, that's fine)")
