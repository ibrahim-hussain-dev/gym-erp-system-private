import frappe
from frappe.utils import flt


def resolve_package_rows(package_name):
    """Expands a Gym Package into its component Gym Plans, with the package's own
    shared duration and computed per-component price already applied."""
    pkg = frappe.get_doc("Gym Package", package_name)
    if pkg.disabled:
        frappe.throw("Package {0} is disabled.".format(pkg.package_name))
    if not pkg.items:
        frappe.throw("Package {0} has no services configured.".format(pkg.package_name))

    entries = []
    for row in pkg.items:
        plan = frappe.db.get_value(
            "Gym Plan", row.gym_plan,
            ["plan_name", "plan_group", "monthly_fee", "sessions", "one_time_charge", "item", "disabled"],
            as_dict=True,
        )
        if not plan:
            frappe.throw("Package component {0} not found.".format(row.gym_plan))
        if plan.disabled:
            frappe.throw("Package component {0} is disabled.".format(plan.plan_name))
        entries.append({"row": row, "plan": plan})

    if pkg.pricing_mode == "Manual Per-Service Price":
        for e in entries:
            e["unit_price"] = flt(e["row"].price)
    elif pkg.pricing_mode == "One Total Price - Equal Split":
        each = flt(pkg.overall_price) / len(entries)
        for e in entries:
            e["unit_price"] = each
    else:  # One Total Price - Proportional Split
        total_weight = sum(flt(e["plan"].monthly_fee) for e in entries) or 1
        for e in entries:
            weight = flt(e["plan"].monthly_fee) / total_weight
            e["unit_price"] = flt(pkg.overall_price) * weight

    resolved = []
    for e in entries:
        plan = e["plan"]
        resolved.append({
            "gym_plan": e["row"].gym_plan,
            "plan_name": plan.plan_name,
            "plan_group": plan.plan_group,
            "item": plan.item,
            "sessions": plan.sessions,
            "one_time_charge": plan.one_time_charge,
            "unit_price": e["unit_price"],
            "duration_value": pkg.duration_value,
            "duration_unit": pkg.duration_unit,
        })
    return resolved
