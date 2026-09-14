import frappe

def run():
    name = frappe.db.get_value("Gym Timing Slot", {"slot_name": "General Hours"}, "name")
    if name:
        doc = frappe.get_doc("Gym Timing Slot", name)
        doc.start_time = "00:00:00"
        doc.end_time = "23:59:59"
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Updated '{name}' -> 00:00:00 - 23:59:59 (poora din cover)")
    else:
        print("General Hours record nahi mila!")
