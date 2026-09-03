import frappe


def run():
    doctype = "Sales Invoice Item"
    frappe.make_property_setter({
        "doctype": doctype,
        "fieldname": "price_list_rate",
        "property": "print_hide",
        "value": "0",
        "property_type": "Check",
    })
    frappe.make_property_setter({
        "doctype": doctype,
        "fieldname": "price_list_rate",
        "property": "in_list_view",
        "value": "1",
        "property_type": "Check",
    })
    frappe.clear_cache(doctype=doctype)
    frappe.db.commit()
    print("Done: Price List Rate column enabled on Sales Invoice print.")
