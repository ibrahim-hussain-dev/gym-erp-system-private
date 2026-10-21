import frappe

def run():
    print("=" * 60)
    print("ALL WORKSPACES")
    print("=" * 60)
    workspaces = frappe.get_all("Workspace", fields=["name", "module", "public", "for_user"])
    for w in workspaces:
        doc = frappe.get_doc("Workspace", w.name)
        roles = [r.role for r in doc.roles] if doc.roles else []
        shortcuts = len(doc.shortcuts) if doc.shortcuts else 0
        print(f"- {w.name} | module={w.module} | public={w.public} | for_user={w.for_user} | restricted_to_roles={roles} | shortcuts={shortcuts}")

    print()
    print("=" * 60)
    print("GYM ROLES -> FULL LIST OF DOCTYPES THEY CAN READ")
    print("=" * 60)
    roles_to_check = ["Gym Front Desk", "Gym Trainer", "Gym Manager"]
    for role in roles_to_check:
        custom_perms = frappe.get_all("Custom DocPerm", filters={"role": role, "read": 1}, fields=["parent"])
        std_perms = frappe.get_all("DocPerm", filters={"role": role, "read": 1}, fields=["parent"])
        all_dts = sorted(set([p.parent for p in custom_perms] + [p.parent for p in std_perms]))
        print(f"\nRole: {role}  ({len(all_dts)} doctypes)")
        for dt in all_dts:
            try:
                mod = frappe.get_meta(dt).module
            except Exception:
                mod = "?"
            print(f"    {dt}  (module: {mod})")

    print()
    print("=" * 60)
    print("CUSTOM PAGES BELONGING TO THIS APP")
    print("=" * 60)
    pages = frappe.get_all("Page", filters={"module": ["like", "%Gym%"]}, fields=["name", "title", "module"])
    for p in pages:
        print(f"- {p.name} | title={p.title} | module={p.module}")
