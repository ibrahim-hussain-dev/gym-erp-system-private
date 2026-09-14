import frappe


def set_perm(doctype, role, **flags):
    existing = frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0})
    if existing:
        frappe.delete_doc("Custom DocPerm", existing, force=True, ignore_permissions=True)
    doc = frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "permlevel": 0,
        "role": role,
        **flags,
    })
    doc.insert(ignore_permissions=True)
    print(f"  Set perm: {doctype} / {role} -> {flags}")


def run():
    print("=== Grant 'Item' read access (Sales Invoice item-detail lookup needs it even with ignore_permissions) ===")
    fd_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=0, share=0)
    mgr_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=1, export=0, print=1, email=0, share=0)
    set_perm("Item", "Gym Front Desk", **fd_readonly)
    set_perm("Item", "Gym Manager", **mgr_readonly)

    print("\n=== Clean up any leftover diagnostic test User ===")
    for email in ("rbac.frontdesk.diag@example.com", "rbac.frontdesk.test@example.com", "rbac.trainer.test@example.com"):
        if frappe.db.exists("User", email):
            try:
                frappe.delete_doc("User", email, force=True, ignore_permissions=True)
                frappe.db.commit()
                print(f"  Removed leftover test user: {email}")
            except Exception as e:
                print(f"  WARNING: could not remove {email}: {e}")
        else:
            print(f"  (not present) {email}")

    frappe.db.commit()
    print("\nDONE")
