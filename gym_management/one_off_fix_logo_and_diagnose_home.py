import frappe

def run():
    nav = frappe.get_single("Navbar Settings")
    nav.app_logo = "/files/Impact logo-01.png"
    nav.save(ignore_permissions=True)
    frappe.db.commit()
    print("FIXED: Navbar Settings.app_logo =", nav.app_logo)

    user_meta = frappe.get_meta("User")
    candidates = [f.fieldname for f in user_meta.fields if "workspace" in f.fieldname.lower() or "home" in f.fieldname.lower()]
    print("User doctype fields mentioning workspace/home:", candidates)

    ss_meta = frappe.get_meta("System Settings")
    ss_candidates = [f.fieldname for f in ss_meta.fields if "home" in f.fieldname.lower()]
    print("System Settings fields mentioning home:", ss_candidates)

    ws_meta = frappe.get_meta("Workspace")
    ws_candidates = [f.fieldname for f in ws_meta.fields if "default" in f.fieldname.lower() or "sequence" in f.fieldname.lower()]
    print("Workspace fields mentioning default/sequence:", ws_candidates)
