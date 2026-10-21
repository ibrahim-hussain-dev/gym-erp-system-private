import frappe

def run():
    # find the Workspace Sidebar record that belongs to "Gym Operations"
    meta = frappe.get_meta("Workspace Sidebar")
    link_field = None
    for f in meta.fields:
        if f.fieldtype == "Link" and f.options == "Workspace":
            link_field = f.fieldname
            break
    print("Link field on Workspace Sidebar pointing to Workspace:", link_field)

    sidebar_name = None
    if link_field:
        sidebar_name = frappe.db.get_value("Workspace Sidebar", {link_field: "Gym Operations"})
    print("Workspace Sidebar record for Gym Operations:", sidebar_name)

    if not sidebar_name:
        print("Could not find it directly, listing all Workspace Sidebar names instead:")
        print(frappe.get_all("Workspace Sidebar", fields=["name"]))
        return

    items = frappe.get_all("Workspace Sidebar Item", filters={"parent": sidebar_name}, fields=["name", "idx", "label", "route", "link_to"])
    print(f"Found {len(items)} items in this sidebar:")
    for i in items:
        print(i)
