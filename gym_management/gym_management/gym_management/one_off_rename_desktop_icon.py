import frappe

def run():
    old_name = "Gym Operations"
    new_name = "Impact Health Studio"
    if frappe.db.exists("Desktop Icon", old_name) and not frappe.db.exists("Desktop Icon", new_name):
        frappe.rename_doc("Desktop Icon", old_name, new_name, force=True)
        frappe.db.commit()
        print(f"Renamed Desktop Icon: {old_name} -> {new_name}")
    else:
        print("Skip: already renamed or not found")

    doc = frappe.get_doc("Desktop Icon", new_name)
    print("name:", doc.name)
    print("label:", doc.label)
    print("logo_url:", doc.logo_url)
    print("link_to:", doc.link_to)

    frappe.clear_cache()
    print("DONE")
