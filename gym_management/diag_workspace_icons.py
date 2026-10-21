import frappe

def run():
    for name in ["Impact Health Studio", "Front Desk"]:
        doc = frappe.get_doc("Workspace", name)
        print(f"{name}: icon={doc.icon!r}")
    from frappe.boot import get_bootinfo
    print()
    print("--- app_data entries mentioning gym or Gym-ERP ---")
    boot = frappe._dict()
    frappe.local.response = frappe._dict()
