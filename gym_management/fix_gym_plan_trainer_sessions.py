import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def run():
    print("=" * 80)
    print("STEP 1: fix trainer Custom Field depends_on so it only shows for Personal Training plans")
    print("=" * 80)
    current_depends_on = frappe.db.get_value("Custom Field", "Gym Plan-trainer", "depends_on")
    print(f"  current depends_on on 'Gym Plan-trainer': {current_depends_on!r}")
    frappe.db.set_value(
        "Custom Field",
        "Gym Plan-trainer",
        "depends_on",
        'eval:doc.plan_group=="Personal Training"',
    )
    new_depends_on = frappe.db.get_value("Custom Field", "Gym Plan-trainer", "depends_on")
    print(f"  new depends_on on 'Gym Plan-trainer': {new_depends_on!r}")

    print()
    print("=" * 80)
    print("STEP 2: hide the 'sessions' field on Gym Plan entirely")
    print("  (feature retired per user; field/column kept as-is since backend still")
    print("   reads plan.sessions in gym_subscription.py / gym_package.py)")
    print("=" * 80)
    existing = frappe.db.exists(
        "Property Setter",
        {"doc_type": "Gym Plan", "field_name": "sessions", "property": "hidden"},
    )
    if existing:
        print(f"  Property Setter already exists: {existing}, updating value to 1")
        frappe.db.set_value("Property Setter", existing, "value", "1")
    else:
        make_property_setter("Gym Plan", "sessions", "hidden", 1, "Check")
        print("  Created Property Setter to hide 'sessions' field on Gym Plan")

    frappe.clear_cache(doctype="Gym Plan")
    frappe.db.commit()

    print()
    print("=" * 80)
    print("STEP 3: verify via fresh meta")
    print("=" * 80)
    meta = frappe.get_meta("Gym Plan")
    for f in meta.fields:
        if f.fieldname in ("trainer", "sessions"):
            print(f"  {f.fieldname}: hidden={f.hidden}, depends_on={f.depends_on!r}")

    print()
    print("DONE.")
