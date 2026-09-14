import frappe

def run():
    print("=== 'gym_member' column in tabSales Invoice (raw DB)? ===")
    cols = frappe.db.sql("SHOW COLUMNS FROM `tabSales Invoice` LIKE 'gym_member'")
    print(cols)

    print("")
    print("=== Custom Field record: Sales Invoice.gym_member ===")
    cf = frappe.db.get_value("Custom Field", {"dt": "Sales Invoice", "fieldname": "gym_member"}, ["name", "fieldtype", "label"], as_dict=True)
    print(cf)

    print("")
    print("=== Last 5 Sales Invoices (name, customer) ===")
    rows = frappe.db.sql("SELECT name, customer, docstatus FROM `tabSales Invoice` ORDER BY creation DESC LIMIT 5", as_dict=True)
    for r in rows:
        print(r)

    print("")
    print("=== Same, trying to select gym_member too ===")
    try:
        rows2 = frappe.db.sql("SELECT name, gym_member FROM `tabSales Invoice` ORDER BY creation DESC LIMIT 5", as_dict=True)
        for r in rows2:
            print(r)
    except Exception as e:
        print("ERROR selecting gym_member:", e)

    print("")
    print("=== Total Gym Subscription records (any status) ===")
    print(frappe.db.count("Gym Subscription"))

    print("")
    print("=== Total Gym Customer Receipt records ===")
    print(frappe.db.count("Gym Customer Receipt"))
