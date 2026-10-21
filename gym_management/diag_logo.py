import frappe

def run():
    files = frappe.get_all("File", filters=[["file_name", "like", "%logo%"]], fields=["name", "file_name", "file_url", "is_private", "attached_to_doctype", "attached_to_name"])
    print("--- File records matching 'logo' ---")
    for f in files:
        print(f)

    print()
    print("--- Website Settings logo fields ---")
    ws = frappe.get_single("Website Settings")
    print("app_logo:", getattr(ws, "app_logo", None))
    print("brand_html:", getattr(ws, "brand_html", None))
    print("banner_image:", getattr(ws, "banner_image", None))

    print()
    print("--- System Settings / Navbar Settings logo-ish fields ---")
    try:
        nb = frappe.get_single("Navbar Settings")
        for f in nb.meta.fields:
            if "logo" in f.fieldname.lower():
                print(f.fieldname, "=", nb.get(f.fieldname))
    except Exception as e:
        print("Navbar Settings error:", e)
