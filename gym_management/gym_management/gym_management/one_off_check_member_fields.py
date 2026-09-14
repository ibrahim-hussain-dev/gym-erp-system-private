import frappe

def run():
    meta = frappe.get_meta("Gym Member")
    fieldnames = [f.fieldname for f in meta.fields]
    print("Gym Member fields:", fieldnames)
    print("auto_renew in fields:", "auto_renew" in fieldnames)
    print("gym_plan in fields:", "gym_plan" in fieldnames)
    print("monthly_fee in fields:", "monthly_fee" in fieldnames)
    print("Gym Invoice doctype exists:", frappe.db.exists("DocType", "Gym Invoice"))
