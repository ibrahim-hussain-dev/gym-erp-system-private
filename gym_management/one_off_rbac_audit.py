import frappe


def run():
    print("=== DocTypes in module Gym-ERP-System ===")
    doctypes = frappe.get_all(
        "DocType",
        filters={"module": "Gym-ERP-System"},
        fields=["name", "istable", "issingle"],
        order_by="name",
    )
    for d in doctypes:
        print(f"  {d.name}  (istable={d.istable}, issingle={d.issingle})")

    print("\n=== Reports in module Gym-ERP-System ===")
    reports = frappe.get_all(
        "Report", filters={"module": "Gym-ERP-System"},
        fields=["name", "report_type", "ref_doctype"], order_by="name"
    )
    for r in reports:
        roles = frappe.get_all("Has Role", filters={"parent": r.name, "parenttype": "Report"}, fields=["role"])
        role_list = [x.role for x in roles] or ["(no role restriction - open to all with doctype read access)"]
        print(f"  {r.name}  type={r.report_type}  ref_doctype={r.ref_doctype}  roles={role_list}")

    print("\n=== Custom Pages (looking for Sell Membership) ===")
    pages = frappe.get_all("Page", filters={"module": "Gym-ERP-System"}, fields=["name", "title"])
    for p in pages:
        roles = frappe.get_all("Has Role", filters={"parent": p.name, "parenttype": "Page"}, fields=["role"])
        role_list = [x.role for x in roles] or ["(open to all)"]
        print(f"  {p.name} ({p.title})  roles={role_list}")

    print("\n=== Workspaces in module Gym-ERP-System ===")
    workspaces = frappe.get_all("Workspace", filters={"module": "Gym-ERP-System"}, fields=["name"])
    for w in workspaces:
        print(f"  {w.name}")

    print("\n=== Existing Custom DocPerm rows on gym doctypes (non-default) ===")
    dt_names = [d.name for d in doctypes if not d.istable]
    custom_perms = frappe.get_all(
        "Custom DocPerm",
        filters={"parent": ["in", dt_names]},
        fields=["parent", "role", "permlevel", "read", "write", "create", "delete", "submit", "cancel", "report", "export"],
        order_by="parent, role",
    )
    if custom_perms:
        for cp in custom_perms:
            print(f"  {cp.parent} / {cp.role} (lvl{cp.permlevel}): read={cp.read} write={cp.write} create={cp.create} delete={cp.delete} submit={cp.submit} cancel={cp.cancel} report={cp.report} export={cp.export}")
    else:
        print("  (none — these doctypes are currently using their default JSON permissions only)")

    print("\n=== Existing Roles (custom, non-standard-Frappe ones) ===")
    all_roles = frappe.get_all("Role", filters={"disabled": 0}, fields=["name", "desk_access"], order_by="name")
    standard_prefixes = ("System Manager", "Administrator", "Guest", "All", "Website", "Accounts", "Sales", "Purchase", "Stock", "HR", "Employee", "Item Manager", "Report Manager", "Analytics", "Customer", "Supplier", "Support", "Projects", "Manufacturing", "Quality", "Maintenance", "Newsletter", "Prepared Report", "Translator", "Dashboard", "Fleet")
    for r in all_roles:
        if not r.name.startswith(standard_prefixes):
            print(f"  {r.name}  (desk_access={r.desk_access})")

    print("\n=== Existing Users (non-Administrator, non-system) ===")
    users = frappe.get_all(
        "User", filters={"user_type": "System User", "name": ["not in", ["Administrator", "Guest"]]},
        fields=["name", "full_name", "enabled"], order_by="name"
    )
    for u in users:
        roles = frappe.get_all("Has Role", filters={"parent": u.name, "parenttype": "User"}, fields=["role"])
        role_list = [x.role for x in roles]
        print(f"  {u.name} ({u.full_name}, enabled={u.enabled})  roles={role_list}")

    print("\n=== Gym Trainer doctype: does it have a 'user' link field? ===")
    meta = frappe.get_meta("Gym Trainer")
    user_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Link" and f.options == "User"]
    print(f"  Link-to-User fields on Gym Trainer: {user_fields or '(none found)'}")
