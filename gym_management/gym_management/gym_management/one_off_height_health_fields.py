import frappe

def run():
    dt = frappe.get_doc("DocType", "Gym Member")

    dt.fields = [f for f in dt.fields if f.fieldname != "height_cm"]
    print("height_cm removed.")

    if not any(f.fieldname == "height_feet" for f in dt.fields):
        idx = next((i for i, f in enumerate(dt.fields) if f.fieldname == "weight_kg"), None)
        new_field = dt.append("fields", {
            "fieldname": "height_feet",
            "fieldtype": "Float",
            "label": "Height (Feet)",
            "description": "e.g. 5.5 for 5 feet 6 inches",
        })
        if idx is not None:
            dt.fields.remove(new_field)
            dt.fields.insert(idx, new_field)
        print("height_feet added.")
    else:
        print("height_feet already exists.")

    if not any(f.fieldname == "health_issue" for f in dt.fields):
        idx2 = next((i for i, f in enumerate(dt.fields) if f.fieldname == "medical_conditions"), None)
        new_field2 = dt.append("fields", {
            "fieldname": "health_issue",
            "fieldtype": "Small Text",
            "label": "Health Issue",
        })
        if idx2 is not None:
            dt.fields.remove(new_field2)
            dt.fields.insert(idx2 + 1, new_field2)
        print("health_issue added.")
    else:
        print("health_issue already exists.")

    dt.save(ignore_permissions=True)
    frappe.db.commit()
    print("DONE - Gym Member updated.")
