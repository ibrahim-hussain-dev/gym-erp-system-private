import frappe

def run():
    print("========== TIMESLOT / TIMING DOCTYPE CHECK ==========")
    candidates = frappe.get_all("DocType", filters=[["name", "like", "%Time%Slot%"]], fields=["name", "module", "custom"])
    candidates += frappe.get_all("DocType", filters=[["name", "like", "%Timing%"]], fields=["name", "module", "custom"])
    seen = []
    for dt in candidates:
        if dt["name"] in seen:
            continue
        seen.append(dt["name"])
        print(f"\n---- '{dt['name']}' ----")
        fields = [f.fieldname for f in frappe.get_meta(dt["name"]).fields]
        print("Fields:", fields)
        sample = frappe.get_all(dt["name"], fields=["name"], limit_page_length=10)
        print("Records:", sample)
    if not seen:
        print("No matching doctype found.")

    print("\n========== GYM MEMBER: preferred_workout_time FIELD ==========")
    meta = frappe.get_meta("Gym Member")
    pwt = meta.get_field("preferred_workout_time")
    if pwt:
        print("Fieldtype:", pwt.fieldtype, "| Options:", pwt.options)
    else:
        print("Field not found")

    print("\n========== GYM MEMBER: gender FIELD ==========")
    gf = meta.get_field("gender")
    if gf:
        print("Fieldtype:", gf.fieldtype, "| Options:", gf.options)
        if gf.fieldtype == "Link" and gf.options:
            recs = frappe.get_all(gf.options, fields=["name"])
            print(f"Records in linked doctype '{gf.options}':", recs)
    else:
        print("Field not found")

    print("\n========== ATTENDANCE-RELATED DOCTYPES ==========")
    dts = frappe.get_all("DocType", filters=[["name", "like", "%Attendance%"]], fields=["name", "module", "custom"])
    print(dts)
    for dt in dts:
        print(f"\n---- Fields of '{dt['name']}' ----")
        fields = [f.fieldname for f in frappe.get_meta(dt["name"]).fields]
        print(fields)
        sample = frappe.get_all(dt["name"], fields=["name"], limit_page_length=3, order_by="creation desc")
        print("Sample:", sample)
