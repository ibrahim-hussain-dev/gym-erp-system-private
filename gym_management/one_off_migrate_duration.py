import frappe


def run():
    plans = frappe.get_all("Gym Plan", fields=["name", "duration_in_months"])
    updated = 0
    for p in plans:
        months = p.duration_in_months or 1
        frappe.db.set_value(
            "Gym Plan", p.name,
            {"duration_value": months, "duration_unit": "Months"},
            update_modified=False,
        )
        updated += 1
    frappe.db.commit()
    print("Backfilled duration_value/duration_unit for {0} Gym Plan(s).".format(updated))
