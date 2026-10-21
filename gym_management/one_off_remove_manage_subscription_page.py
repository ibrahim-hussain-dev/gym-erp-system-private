import frappe
import subprocess

def run():
    if frappe.db.exists("Page", "manage-subscription"):
        frappe.delete_doc("Page", "manage-subscription", ignore_permissions=True, force=True)
        frappe.db.commit()
        print("Deleted Page: manage-subscription")
    else:
        print("Page record already absent")

    result = subprocess.run([
        "mv",
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/page/manage_subscription",
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/page/_deprecated_manage_subscription"
    ], capture_output=True, text=True)
    print("Moved page folder aside:", result.returncode == 0, result.stderr)
