import frappe

def run():
    print("=" * 60)
    print("1. Any DocType with 'Sidebar' in the name?")
    print("=" * 60)
    print(frappe.get_all("DocType", filters={"name": ["like", "%Sidebar%"]}, fields=["name"]))

    print()
    print("=" * 60)
    print("2. __UserSettings rows for Administrator mentioning Workspace/manage-subscription")
    print("=" * 60)
    rows = frappe.db.sql("""
        select `user`, `doctype`, `data`
        from `__UserSettings`
        where `user` = 'Administrator'
        and (`data` like '%%manage-subscription%%' or `data` like '%%Membership Retention%%' or `doctype` like '%%Workspace%%')
    """, as_dict=True)
    for r in rows:
        print(f"user={r.user} doctype={r.doctype}")
        print(r.data)
        print("---")

    print()
    print("=" * 60)
    print("3. Any field on User doctype mentioning 'sidebar'")
    print("=" * 60)
    meta = frappe.get_meta("User")
    for f in meta.fields:
        if "sidebar" in f.fieldname.lower():
            print(f.fieldname, f.label, f.fieldtype)
