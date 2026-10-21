import frappe

def set_property(doctype, fieldname, property, value, property_type):
    name = frappe.db.get_value(
        "Property Setter",
        {"doc_type": doctype, "field_name": fieldname, "property": property},
    )
    if name:
        frappe.db.set_value("Property Setter", name, "value", value)
    else:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": doctype,
            "field_name": fieldname,
            "property": property,
            "value": value,
            "property_type": property_type,
        }).insert(ignore_permissions=True)

def run():
    if not frappe.db.exists("Custom Field", {"dt": "Gym Package Item", "fieldname": "plan_price"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Gym Package Item",
            "fieldname": "plan_price",
            "label": "Normal Price",
            "fieldtype": "Currency",
            "insert_after": "gym_plan",
            "read_only": 1,
        }).insert(ignore_permissions=True)
        print("Added plan_price field to Gym Package Item.")
    else:
        print("plan_price field already exists, skipping.")

    set_property("Gym Package Item", "price", "label", "Price for this Service", "Data")
    set_property(
        "Gym Package Item", "price", "read_only_depends_on",
        'eval:parent.pricing_mode!="Manual Per-Service Price"', "Code"
    )
    set_property(
        "Gym Package", "overall_price", "read_only_depends_on",
        'eval:doc.pricing_mode=="Manual Per-Service Price"', "Code"
    )
    set_property(
        "Gym Package", "overall_price", "description",
        "Manual mode: auto-calculated as the sum of the service prices below. Split modes: type your target total price here \u2014 it will be divided among the services.",
        "Text"
    )
    frappe.db.commit()
    print("Property setters applied.")
