import frappe

def run():
    items = frappe.get_all("Workspace Sidebar Item", filters={"parent": "Gym Operations"}, fields=["name", "idx", "label", "route", "link_to"])
    print(f"Found {len(items)} items:")
    for i in items:
        print(i)
