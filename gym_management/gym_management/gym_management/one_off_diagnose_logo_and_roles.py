import frappe

def run():
    ws = frappe.get_single("Website Settings")
    print("=== Website Settings ===")
    print("app_logo:", ws.get("app_logo"))
    print("banner_image:", ws.get("banner_image"))
    print("app_name:", ws.get("app_name"))

    if frappe.db.exists("DocType", "Navbar Settings"):
        nav = frappe.get_single("Navbar Settings")
        print("=== Navbar Settings ===")
        for f in nav.meta.fields:
            print(f.fieldname, "=", nav.get(f.fieldname))
    else:
        print("Navbar Settings doctype not found")

    print("=== Workspace 'roles' child table structure ===")
    ws_meta = frappe.get_meta("Workspace")
    roles_field = [f for f in ws_meta.fields if f.fieldname == "roles"][0]
    print("child doctype:", roles_field.options)
    child_meta = frappe.get_meta(roles_field.options)
    print("child fields:", [f.fieldname for f in child_meta.fields])

    print("=== Recently uploaded files (to find the logo) ===")
    files2 = frappe.get_all("File", order_by="creation desc", limit=10,
        fields=["name", "file_name", "file_url", "is_private", "attached_to_doctype", "attached_to_name", "creation"])
    for f in files2:
        print(f)
