import frappe

def run():
    doctypes = [
        "Gym Member", "Gym Plan", "Gym Package", "Gym Trainer", "Gym Timing Slot",
        "Gym Slot", "Gym Subscription", "Gym Attendance", "Gym Fitness Log",
        "Gym Expense", "Sales Invoice", "Payment Entry",
    ]
    print("=" * 70)
    print("DATA INVENTORY (Gym Timing Slot will be KEPT regardless — shown for info only)")
    print("=" * 70)
    for dt in doctypes:
        if not frappe.db.exists("DocType", dt):
            print(f"  {dt:20} -- doctype does not exist, skipping")
            continue
        total = frappe.db.count(dt)
        submitted = 0
        if frappe.get_meta(dt).is_submittable:
            submitted = frappe.db.count(dt, {"docstatus": 1})
        print(f"  {dt:20} total={total:5}  submitted(docstatus=1)={submitted}")

    print()
    print("--- Users linked to Gym Trainer (via linked_user), excluding Administrator/Guest ---")
    trainers = frappe.get_all("Gym Trainer", fields=["name", "linked_user"])
    for t in trainers:
        if t.linked_user:
            print(f"  Trainer {t.name} -> User {t.linked_user}")
