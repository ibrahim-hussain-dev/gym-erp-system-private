import frappe

def run():
    print("=== Item Price: Custom DocPerm rows ===")
    rows = frappe.get_all("Custom DocPerm", filters={"parent": "Item Price"},
        fields=["role", "read", "write", "create", "delete", "submit"])
    for r in rows:
        print(r)

    print("")
    print("=== Item Price: standard permissions (from meta) ===")
    meta = frappe.get_meta("Item Price")
    for p in meta.permissions:
        print({"role": p.role, "read": p.read, "write": p.write, "create": p.create, "delete": p.delete})

    print("")
    print("=== Roles assigned to iibrahimhere@gmail.com ===")
    print(frappe.get_roles("iibrahimhere@gmail.com"))
