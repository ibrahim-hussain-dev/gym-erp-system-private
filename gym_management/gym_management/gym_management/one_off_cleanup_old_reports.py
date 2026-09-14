import frappe

def run():
    for name in ["Gym Master Report", "Gym Monthly Income"]:
        if frappe.db.exists("Report", name):
            frappe.delete_doc("Report", name, force=True, ignore_permissions=True)
            print(f"Deleted broken report: {name}")
        else:
            print(f"Not found (already gone): {name}")
    frappe.db.commit()
