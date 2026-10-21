import frappe

def run():
    for dt in ["Gym Branch", "Gym Trainer Availability"]:
        if not frappe.db.exists("DocType", dt):
            print(f"  {dt:25} -- doctype does not exist")
            continue
        total = frappe.db.count(dt)
        print(f"  {dt:25} total={total}")
