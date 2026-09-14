import frappe

def run():
    dt = frappe.get_doc("DocType", "Gym Member")

    # Add Activity Level
    if "activity_level" not in [f.fieldname for f in dt.fields]:
        dt.append("fields", {
            "fieldname": "activity_level",
            "fieldtype": "Select",
            "label": "Activity Level",
            "options": "Sedentary\nLightly Active\nModerately Active\nVery Active",
        })
        new_field = dt.fields[-1]
        dt.fields.remove(new_field)
        idx = [f.fieldname for f in dt.fields].index("fitness_goal") + 1
        dt.fields.insert(idx, new_field)
        print("Added activity_level field")
    else:
        print("activity_level already exists, skipping")

    # Add Workout History
    if "workout_history" not in [f.fieldname for f in dt.fields]:
        dt.append("fields", {
            "fieldname": "workout_history",
            "fieldtype": "Select",
            "label": "Workout History",
            "options": "Newbie\nBeginner\nIntermediate\nAdvanced",
        })
        new_field = dt.fields[-1]
        dt.fields.remove(new_field)
        idx = [f.fieldname for f in dt.fields].index("activity_level") + 1
        dt.fields.insert(idx, new_field)
        print("Added workout_history field")
    else:
        print("workout_history already exists, skipping")

    dt.save(ignore_permissions=True)
    print("Gym Member doctype saved successfully")
