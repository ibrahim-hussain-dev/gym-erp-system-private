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
    print("=== Step 1: Grant 'Account' read access (needed for Sales Invoice GL/tax processing) ===")
    fd_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=0, share=0)
    mgr_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=1, export=0, print=1, email=0, share=0)
    set_perm("Account", "Gym Front Desk", **fd_readonly)
    set_perm("Account", "Gym Manager", **mgr_readonly)

    print("\n=== Step 2: Clean up leftover test data from the failed positive-sale test ===")
    for email_pattern in ["frontdesk.positive.%"]:
        members = frappe.get_all("Gym Member", filters={"email": ["like", email_pattern]}, pluck="name")
        for member_name in members:
            try:
                customer = frappe.db.get_value("Gym Member", member_name, "customer")
                for sub in frappe.get_all("Gym Subscription", filters={"member": member_name}):
                    subdoc = frappe.get_doc("Gym Subscription", sub.name)
                    if subdoc.docstatus == 1:
                        subdoc.cancel()
                    frappe.delete_doc("Gym Subscription", sub.name, force=True, ignore_permissions=True)
                for inv in frappe.get_all("Sales Invoice", filters={"gym_member": member_name}):
                    invdoc = frappe.get_doc("Sales Invoice", inv.name)
                    if invdoc.docstatus == 1:
                        invdoc.cancel()
                    frappe.delete_doc("Sales Invoice", inv.name, force=True, ignore_permissions=True)
                frappe.db.commit()
                # Fetch a fresh doc right before deleting to dodge the timestamp-mismatch error
                frappe.delete_doc("Gym Member", member_name, force=True, ignore_permissions=True)
                frappe.db.commit()
                if customer:
                    for contact_link in frappe.get_all(
                        "Dynamic Link",
                        filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Contact"},
                        pluck="parent",
                    ):
                        try:
                            frappe.delete_doc("Contact", contact_link, force=True, ignore_permissions=True)
                        except Exception:
                            pass
                    try:
                        frappe.delete_doc("Customer", customer, force=True, ignore_permissions=True)
                    except Exception:
                        pass
                frappe.db.commit()
                print(f"  Cleaned up leftover test member: {member_name}")
            except Exception as e:
                print(f"  WARNING: could not fully clean up {member_name}: {e}")

    frappe.db.commit()
    print("\n=== DONE ===")
