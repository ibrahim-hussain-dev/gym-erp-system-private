import frappe

def run():
    slot_dt = frappe.get_doc("DocType", "Gym Timing Slot")
    if slot_dt.title_field != "slot_name":
        slot_dt.title_field = "slot_name"
        slot_dt.save(ignore_permissions=True)
        print("Gym Timing Slot: title_field set to slot_name")

    def upsert_slot(old_name_guess, slot_name, gender, start_time, end_time):
        existing = frappe.db.get_value("Gym Timing Slot", {"slot_name": old_name_guess}, "name")
        doc = frappe.get_doc("Gym Timing Slot", existing) if existing else frappe.new_doc("Gym Timing Slot")
        doc.slot_name = slot_name
        doc.gender = gender
        doc.day_from = "Monday"
        doc.day_to = "Sunday"
        doc.start_time = start_time
        doc.end_time = end_time
        doc.disabled = 0
        doc.save(ignore_permissions=True)
        print(f"Saved: {doc.name} -> {slot_name} ({gender}, {start_time}-{end_time})")

    upsert_slot("General Hours", "Morning Mixed Hours (7:00 AM - 12:00 PM)", "Mixed", "07:00:00", "12:00:00")
    upsert_slot("Ladies Hours", "Ladies Hours (12:00 PM - 4:00 PM)", "Female", "12:00:00", "16:00:00")
    upsert_slot("Evening Mixed Hours", "Evening Mixed Hours (4:00 PM - 11:00 PM)", "Mixed", "16:00:00", "23:00:00")
    frappe.db.commit()

    dt = frappe.get_doc("DocType", "Gym Member")
    if not any(f.fieldname == "alternative_workout_time" for f in dt.fields):
        idx = next((i for i, f in enumerate(dt.fields) if f.fieldname == "preferred_workout_time"), None)
        new_field = dt.append("fields", {
            "fieldname": "alternative_workout_time",
            "fieldtype": "Link",
            "label": "Alternative Training Slot",
            "options": "Gym Timing Slot",
            "description": "Optional second allowed slot for flexible-schedule members (e.g. office/university).",
        })
        if idx is not None:
            dt.fields.remove(new_field)
            dt.fields.insert(idx + 1, new_field)
        dt.save(ignore_permissions=True)
        print("Gym Member: alternative_workout_time field added.")
    else:
        print("Gym Member: alternative_workout_time already exists.")

    frappe.db.commit()
    print("DONE.")
