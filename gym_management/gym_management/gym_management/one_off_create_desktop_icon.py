import frappe

def run():
    print("=== Check Workspace Sidebar doctype ===")
    exists_dt = frappe.db.exists("DocType", "Workspace Sidebar")
    print("Workspace Sidebar DocType exists:", exists_dt)
    if exists_dt:
        rows = frappe.get_all("Workspace Sidebar", filters={"name": ["like", "%Gym%"]}, fields=["name"])
        print("Matches for 'Gym':", rows)
        rows_all = frappe.get_all("Workspace Sidebar", fields=["name"], limit=10)
        print("Sample Workspace Sidebar names:", rows_all)

    if frappe.db.exists("Desktop Icon", {"label": "Gym Operations"}):
        print("Desktop Icon already exists, skipping creation")
        frappe.clear_cache()
        return

    max_idx = frappe.db.sql("select max(idx) from `tabDesktop Icon`")[0][0] or 0

    try:
        doc = frappe.get_doc({
            "doctype": "Desktop Icon",
            "label": "Gym Operations",
            "icon_type": "Link",
            "link_type": "Workspace Sidebar",
            "link_to": "Gym Operations",
            "app": "gym_management",
            "logo_url": "/private/files/impact_logo_512.png",
            "hidden": 0,
            "standard": 0,
            "restrict_removal": 0,
            "bg_color": "blue",
            "idx": (max_idx or 0) + 1,
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Desktop Icon:", doc.name)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("FAILED:", e)

    frappe.clear_cache()
    print("DONE")
