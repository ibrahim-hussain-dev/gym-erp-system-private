import frappe

def run():
    # 1. Rename Gym Manager -> Gym Owner (cascades to all permissions/reports/pages/user roles automatically)
    if frappe.db.exists("Role", "Gym Manager") and not frappe.db.exists("Role", "Gym Owner"):
        frappe.rename_doc("Role", "Gym Manager", "Gym Owner", force=True)
        print("Renamed role: Gym Manager -> Gym Owner")
    else:
        print("Skip rename (already done or Gym Manager missing)")

    # 2. Create Temporary Developer role (label only; System Manager is what actually unlocks backend)
    if not frappe.db.exists("Role", "Temporary Developer"):
        frappe.get_doc({"doctype": "Role", "role_name": "Temporary Developer", "desk_access": 1}).insert(ignore_permissions=True)
        print("Created role: Temporary Developer")

    # 3. Fix the developer/test account -> full access everywhere (backend + app)
    dev_email = "iibrahimhere@gmail.com"
    user = frappe.get_doc("User", dev_email)
    keep = {"System Manager", "Gym Owner", "Temporary Developer"}
    user.roles = [r for r in user.roles if r.role in keep]
    existing = {r.role for r in user.roles}
    for role in keep:
        if role not in existing:
            user.append("roles", {"role": role})
    user.save(ignore_permissions=True)
    print("Developer account roles now:", [r.role for r in user.roles])

    # 4. Close the gap: remove Front Desk from Cash Collection Report
    rpt = frappe.get_doc("Report", "Gym Cash Collection Report")
    before = [r.role for r in rpt.roles]
    rpt.roles = [r for r in rpt.roles if r.role != "Gym Front Desk"]
    if not any(r.role == "Gym Owner" for r in rpt.roles):
        rpt.append("roles", {"role": "Gym Owner"})
    rpt.save(ignore_permissions=True)
    print("Gym Cash Collection Report roles:", before, "->", [r.role for r in rpt.roles])

    # 5. Make sure the other financial reports stay Owner-only (never Front Desk)
    for report_name in ["Gym Member Retention", "Gym Membership Status", "Gym Monthly Revenue", "Gym Revenue by Plan", "Gym Trainer Commission"]:
        if frappe.db.exists("Report", report_name):
            r = frappe.get_doc("Report", report_name)
            r.roles = [x for x in r.roles if x.role != "Gym Front Desk"]
            if not any(x.role == "Gym Owner" for x in r.roles):
                r.append("roles", {"role": "Gym Owner"})
            r.save(ignore_permissions=True)
            print(report_name, "roles ->", [x.role for x in r.roles])

    # 6. Gym Expense: Front Desk can CREATE entries but never read/browse them
    dt, role = "Gym Expense", "Gym Front Desk"
    existing_perm = frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role, "permlevel": 0})
    if existing_perm:
        frappe.delete_doc("Custom DocPerm", existing_perm, force=True, ignore_permissions=True)
    frappe.get_doc({
        "doctype": "Custom DocPerm", "parent": dt, "parenttype": "DocType", "parentfield": "permissions",
        "permlevel": 0, "role": role,
        "read": 0, "write": 0, "create": 1, "delete": 0, "submit": 0, "cancel": 0,
        "report": 0, "export": 0, "print": 0, "email": 0, "share": 0,
    }).insert(ignore_permissions=True)
    print(f"{dt}: {role} is now create-only (no read/browse)")

    # 7. Let Front Desk open the Record Expense page (needed to actually create step 6's entries)
    pg = frappe.get_doc("Page", "record-expense")
    if not any(r.role == "Gym Front Desk" for r in pg.roles):
        pg.append("roles", {"role": "Gym Front Desk"})
        pg.save(ignore_permissions=True)
        print("record-expense page: added Gym Front Desk")
    else:
        print("record-expense page: Gym Front Desk already present")

    frappe.clear_cache()
    frappe.db.commit()
    print("DONE")
