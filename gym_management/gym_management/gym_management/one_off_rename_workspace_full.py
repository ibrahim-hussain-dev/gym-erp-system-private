import frappe

def run():
    old_name = "Gym Operations"
    new_name = "Impact Health Studio"

    if frappe.db.exists("Workspace", old_name) and not frappe.db.exists("Workspace", new_name):
        frappe.rename_doc("Workspace", old_name, new_name, force=True)
        frappe.db.commit()
        print(f"Renamed Workspace: {old_name} -> {new_name}")
    else:
        print("Workspace rename skipped (already renamed or not found)")

    if frappe.db.exists("Workspace Sidebar", old_name) and not frappe.db.exists("Workspace Sidebar", new_name):
        frappe.rename_doc("Workspace Sidebar", old_name, new_name, force=True)
        frappe.db.commit()
        print(f"Renamed Workspace Sidebar: {old_name} -> {new_name}")
    else:
        print("Workspace Sidebar rename skipped (already renamed or not found)")

    if frappe.db.exists("Desktop Icon", old_name):
        di = frappe.get_doc("Desktop Icon", old_name)
        di.label = new_name
        di.link_to = new_name
        di.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated old-named Desktop Icon label/link_to")
    elif frappe.db.exists("Desktop Icon", new_name):
        di = frappe.get_doc("Desktop Icon", new_name)
        if di.label != new_name or di.link_to != new_name:
            di.label = new_name
            di.link_to = new_name
            di.save(ignore_permissions=True)
            frappe.db.commit()
        print("Desktop Icon already using new name, confirmed label/link_to")
    else:
        print("WARNING: Desktop Icon record not found by either name")

    if frappe.db.exists("Workspace Sidebar", new_name):
        ws_sidebar = frappe.get_doc("Workspace Sidebar", new_name)
        changed = False
        for item in ws_sidebar.items:
            if item.link_type == "Workspace" and item.link_to == old_name:
                item.link_to = new_name
                changed = True
            if item.label == old_name:
                item.label = new_name
                changed = True
        if changed:
            ws_sidebar.save(ignore_permissions=True)
            frappe.db.commit()
            print("Fixed internal Workspace Sidebar self-link item")

    frappe.clear_cache()
    print("DONE")
