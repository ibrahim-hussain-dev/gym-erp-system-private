import frappe

def run():
    candidates = ["Website Settings", "Navbar Settings", "System Settings"]
    for dt in candidates:
        try:
            doc = frappe.get_single(dt)
            for f in doc.meta.fields:
                val = doc.get(f.fieldname)
                if isinstance(val, str) and "private/files" in val:
                    print(f"{dt}.{f.fieldname} = {val!r}")
        except Exception as e:
            print(dt, "error:", e)

    print()
    print("--- File records matching 'logo' (name / url / is_private) ---")
    files = frappe.get_all("File", filters=[["file_name", "like", "%logo%"]], fields=["name", "file_url", "is_private"])
    for f in files:
        print(f)

    print()
    print("--- Website Settings favicon / splash / app_logo fields ---")
    ws = frappe.get_single("Website Settings")
    for fn in ["favicon", "splash_image", "banner_image", "app_logo"]:
        print(fn, "=", ws.get(fn))
