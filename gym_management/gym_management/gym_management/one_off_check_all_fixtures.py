import frappe

def run():
    hooks_module = frappe.get_module("gym_management.hooks")
    fixtures = getattr(hooks_module, "fixtures", [])
    print("=== Declared fixtures in hooks.py ===")
    for fx in fixtures:
        doctype = fx["doctype"]
        filters = fx.get("filters")
        print(f"\n-- {doctype} where {filters}")
        rows = frappe.get_all(doctype, filters=filters, fields=["name"])
        if rows:
            for r in rows:
                print("   FOUND:", r.name)
        else:
            print("   MISSING (no matching record in DB!)")
