import frappe

def run():
    print("========== GYM TIMING SLOT — FULL FIELD META ==========")
    meta = frappe.get_meta("Gym Timing Slot")
    for f in meta.fields:
        print(f"{f.fieldname:20s} | {f.fieldtype:12s} | options: {f.options}")

    print("\n========== GYM MEMBER — GENDER VALUE COUNTS ==========")
    print(frappe.db.sql("select gender, count(*) as c from `tabGym Member` group by gender", as_dict=True))

    print("\n========== GYM MEMBER — preferred_workout_time VALUE COUNTS ==========")
    print(frappe.db.sql("select preferred_workout_time, count(*) as c from `tabGym Member` group by preferred_workout_time", as_dict=True))

    print("\n========== GYM ATTENDANCE — RECORD COUNT ==========")
    print("Total:", frappe.db.count("Gym Attendance"))
