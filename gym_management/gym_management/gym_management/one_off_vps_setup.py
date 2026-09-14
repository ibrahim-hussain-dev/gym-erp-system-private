import frappe

def run():
    # Rename company from "Impact Health" to "Gym ERP" (matches hardcoded references in api.py)
    if frappe.db.exists("Company", "Impact Health") and not frappe.db.exists("Company", "Gym ERP"):
        frappe.rename_doc("Company", "Impact Health", "Gym ERP", force=True)
        frappe.db.commit()
        print("Renamed company: Impact Health -> Gym ERP")
    elif frappe.db.exists("Company", "Gym ERP"):
        print("Company 'Gym ERP' already exists, skipping rename")
    else:
        print("WARNING: Neither 'Impact Health' nor 'Gym ERP' company found - please check manually")

    gd = frappe.get_single("Global Defaults")
    if gd.default_company != "Gym ERP" and frappe.db.exists("Company", "Gym ERP"):
        gd.default_company = "Gym ERP"
        gd.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated Global Defaults default_company -> Gym ERP")

    # Create the remaining Number Card
    if not frappe.db.exists("Number Card", "Today's Cash Collected"):
        frappe.get_doc({
            "doctype": "Number Card",
            "label": "Today's Cash Collected",
            "document_type": "Payment Entry",
            "function": "Sum",
            "aggregate_function_based_on": "paid_amount",
            "filters_json": frappe.as_json([
                ["Payment Entry", "docstatus", "=", 1],
                ["Payment Entry", "payment_type", "=", "Receive"],
                ["Payment Entry", "company", "=", "Gym ERP"],
                ["Payment Entry", "posting_date", "=", "Today"],
            ]),
            "is_public": 1,
            "show_percentage_stats": 0,
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Number Card: Today's Cash Collected")
    else:
        print("Number Card already exists: Today's Cash Collected")

    print("DONE")
