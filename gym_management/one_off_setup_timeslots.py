import frappe

def run():
    # 1) Gym Member doctype: preferred_workout_time -> Link, gender options trim
    dt = frappe.get_doc("DocType", "Gym Member")
    for f in dt.fields:
        if f.fieldname == "preferred_workout_time":
            f.fieldtype = "Link"
            f.options = "Gym Timing Slot"
            print("preferred_workout_time -> Link(Gym Timing Slot)")
        if f.fieldname == "gender":
            f.options = "Male\nFemale"
            print("gender options -> Male/Female only")
    dt.save(ignore_permissions=True)

    # 2) Purani text values (Morning/Evening/Afternoon/Any) clear karo
    frappe.db.sql("""
        UPDATE `tabGym Member`
        SET preferred_workout_time = NULL
        WHERE preferred_workout_time IN ('Morning','Afternoon','Evening','Any')
    """)
    print("Old preferred_workout_time text values cleared.")

    # 3) Do default Gym Timing Slot records
    if not frappe.db.exists("Gym Timing Slot", {"slot_name": "Ladies Hours"}):
        frappe.get_doc({
            "doctype": "Gym Timing Slot",
            "slot_name": "Ladies Hours",
            "gender": "Female",
            "day_from": "Monday",
            "day_to": "Sunday",
            "start_time": "11:00:00",
            "end_time": "15:00:00",
            "disabled": 0,
        }).insert(ignore_permissions=True)
        print("Created: Ladies Hours (11:00 AM - 3:00 PM)")

    if not frappe.db.exists("Gym Timing Slot", {"slot_name": "General Hours"}):
        frappe.get_doc({
            "doctype": "Gym Timing Slot",
            "slot_name": "General Hours",
            "gender": "Mixed",
            "day_from": "Monday",
            "day_to": "Sunday",
            "start_time": "06:00:00",
            "end_time": "23:00:00",
            "disabled": 0,
        }).insert(ignore_permissions=True)
        print("Created: General Hours (6:00 AM - 11:00 PM)")

    frappe.db.commit()
    print("DONE.")
