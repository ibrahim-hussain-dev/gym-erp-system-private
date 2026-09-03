import frappe

FRONT_DESK = "Gym Front Desk"
TRAINER = "Gym Trainer"
MANAGER = "Gym Manager"


def ensure_role(role_name):
    if not frappe.db.exists("Role", role_name):
        frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)
        print(f"Created Role: {role_name}")
    else:
        print(f"Role already exists: {role_name}")


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


def restrict_report(report_name, roles):
    doc = frappe.get_doc("Report", report_name)
    doc.set("roles", [])
    for r in roles:
        doc.append("roles", {"role": r})
    doc.save(ignore_permissions=True)
    print(f"Restricted Report '{report_name}' to roles: {roles}")


def restrict_page(page_name, roles):
    doc = frappe.get_doc("Page", page_name)
    doc.set("roles", [])
    for r in roles:
        doc.append("roles", {"role": r})
    doc.save(ignore_permissions=True)
    print(f"Restricted Page '{page_name}' to roles: {roles}")


def run():
    print("=== Step 1: Create roles ===")
    for r in (FRONT_DESK, TRAINER, MANAGER):
        ensure_role(r)

    print("\n=== Step 2: Front Desk - operational doctypes (create/read/write, no delete) ===")
    fd_full = dict(read=1, write=1, create=1, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=1, share=0)
    for dt in ["Gym Member", "Gym Fitness Log", "Gym Slot", "Gym Attendance", "Gym Quotation"]:
        set_perm(dt, FRONT_DESK, **fd_full)

    fd_rw_nocreate = dict(read=1, write=1, create=0, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=1, share=0)
    set_perm("Gym Subscription", FRONT_DESK, **fd_rw_nocreate)

    print("\n=== Step 3: Front Desk - reference data (read only, no edit) ===")
    fd_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=0, share=0)
    for dt in ["Gym Plan", "Gym Package", "Gym Promo Code", "Gym Trainer", "Gym Branch", "Gym Timing Slot"]:
        set_perm(dt, FRONT_DESK, **fd_readonly)

    print("\n=== Step 4: Front Desk - invoicing & payment (no cancel/delete, no bulk export) ===")
    fd_invoice = dict(read=1, write=1, create=1, delete=0, submit=1, cancel=0, amend=0, report=0, export=0, print=1, email=1, share=0)
    set_perm("Sales Invoice", FRONT_DESK, **fd_invoice)
    set_perm("Payment Entry", FRONT_DESK, **fd_invoice)
    set_perm("Gym Payment Entry", FRONT_DESK, **fd_invoice)
    set_perm("Customer", FRONT_DESK, **fd_readonly)

    print("\n=== Step 5: Gym Expense stays Manager-only (front desk gets nothing here) ===")

    print("\n=== Step 6: Trainer - self-view only (read-only for now) ===")
    trainer_readonly = dict(read=1, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, report=0, export=0, print=1, email=0, share=0)
    set_perm("Gym Slot", TRAINER, **trainer_readonly)
    set_perm("Gym Trainer", TRAINER, **trainer_readonly)

    print("\n=== Step 7: Gym Manager - full access ===")
    mgr_full = dict(read=1, write=1, create=1, delete=1, submit=1, cancel=1, amend=1, report=1, export=1, print=1, email=1, share=1)
    for dt in [
        "Gym Attendance", "Gym Branch", "Gym Expense", "Gym Fitness Log", "Gym Member",
        "Gym Package", "Gym Payment Entry", "Gym Plan", "Gym Promo Code", "Gym Quotation",
        "Gym Slot", "Gym Subscription", "Gym Timing Slot", "Gym Trainer",
        "Sales Invoice", "Payment Entry", "Customer",
    ]:
        set_perm(dt, MANAGER, **mgr_full)

    print("\n=== Step 8: Restrict the 5 financial/sensitive reports to Gym Manager only ===")
    for report_name in [
        "Gym Membership Retention", "Gym Membership Status", "Gym Monthly Revenue",
        "Gym Revenue by Plan", "Gym Trainer Commission",
    ]:
        restrict_report(report_name, [MANAGER])

    print("\n=== Step 9: Restrict custom pages ===")
    restrict_page("sell-membership", [FRONT_DESK, MANAGER])
    restrict_page("book-pt-session", [FRONT_DESK, MANAGER])
    restrict_page("mark-attendance", [FRONT_DESK, MANAGER])
    restrict_page("manage-subscription", [FRONT_DESK, MANAGER])
    restrict_page("record-expense", [MANAGER])

    print("\n=== Step 10: Add 'linked_user' field to Gym Trainer (for future self-view setup) ===")
    if not frappe.db.exists("Custom Field", {"dt": "Gym Trainer", "fieldname": "linked_user"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Gym Trainer",
            "fieldname": "linked_user",
            "label": "Linked User Account",
            "fieldtype": "Link",
            "options": "User",
            "description": "Link this trainer to their login account so they only see their own PT sessions and commission.",
        }).insert(ignore_permissions=True)
        print("  Added 'linked_user' field to Gym Trainer.")
    else:
        print("  'linked_user' field already exists on Gym Trainer.")

    frappe.db.commit()
    print("\n=== RBAC SETUP COMPLETE ===")
