import frappe


def run():
    fields = [
        {
            "dt": "Sales Invoice Item",
            "fieldname": "gym_package_duration_value",
            "label": "Gym Package Duration Value",
            "fieldtype": "Int",
            "insert_after": "item_name",
            "hidden": 1,
            "print_hide": 1,
        },
        {
            "dt": "Sales Invoice Item",
            "fieldname": "gym_package_duration_unit",
            "label": "Gym Package Duration Unit",
            "fieldtype": "Select",
            "options": "\nDays\nWeeks\nMonths",
            "insert_after": "gym_package_duration_value",
            "hidden": 1,
            "print_hide": 1,
        },
    ]
    for f in fields:
        if frappe.db.exists("Custom Field", {"dt": f["dt"], "fieldname": f["fieldname"]}):
            continue
        frappe.get_doc({"doctype": "Custom Field", **f}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Custom fields created on Sales Invoice Item for package duration override.")
