import frappe

# Read-only. Checking whether Sales Invoice Item's own
# gym_package_duration_value / gym_package_duration_unit custom fields are
# carrying a bad default (e.g. 1 / "Days") that silently overrides the real
# Gym Plan duration in create_subscription_from_invoice()'s:
#   duration_value = item.get("gym_package_duration_value") or plan.duration_value
#   duration_unit = item.get("gym_package_duration_unit") or plan.duration_unit


def run():
    print("=== Custom Field config: gym_package_duration_value / gym_package_duration_unit on Sales Invoice Item ===")
    rows = frappe.get_all(
        "Custom Field",
        filters={"dt": "Sales Invoice Item", "fieldname": ["in", ["gym_package_duration_value", "gym_package_duration_unit"]]},
        fields=["fieldname", "fieldtype", "options", "default", "reqd", "hidden", "read_only"],
    )
    for r in rows:
        print(f"  {r}")

    print()
    print("=== Gym Plan: duration_value / duration_unit for all plans (ground truth) ===")
    plans = frappe.get_all(
        "Gym Plan",
        fields=["name", "plan_name", "duration_value", "duration_unit", "item", "one_time_charge"],
        order_by="name",
    )
    for p in plans:
        print(f"  {p}")

    print()
    print("=== Last 15 Gym Subscriptions: start_date, end_date, plan's real duration, vs item's stored duration fields ===")
    subs = frappe.get_all(
        "Gym Subscription",
        fields=["name", "member", "gym_plan", "start_date", "end_date", "status", "sales_invoice_item", "sales_invoice"],
        order_by="creation desc",
        limit=15,
    )
    for s in subs:
        plan = frappe.db.get_value(
            "Gym Plan", s.gym_plan, ["duration_value", "duration_unit"], as_dict=True
        ) if s.gym_plan else None
        item_duration = None
        if s.sales_invoice_item:
            item_duration = frappe.db.get_value(
                "Sales Invoice Item", s.sales_invoice_item,
                ["gym_package_duration_value", "gym_package_duration_unit", "item_code", "qty"],
                as_dict=True,
            )
        same_day = s.start_date == s.end_date
        print(f"  {s.name}: start={s.start_date} end={s.end_date} SAME_DAY={same_day}")
        print(f"      gym_plan={s.gym_plan!r} plan_duration={plan}")
        print(f"      sales_invoice_item={s.sales_invoice_item!r} item_duration_fields={item_duration}")
        print()
