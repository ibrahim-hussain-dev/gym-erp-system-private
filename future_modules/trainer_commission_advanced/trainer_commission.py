import frappe
from frappe.utils import flt, nowdate


def log_commission_from_invoice(doc, method=None):
    """Fires on Sales Invoice submit. For each line item that maps to a Gym Plan
    with an assigned Trainer, log a one-time commission = line amount x trainer's
    commission %, and add it to that trainer's running total. No session-counting."""
    for item in doc.items:
        plan = frappe.db.get_value(
            "Gym Plan", {"item": item.item_code},
            ["name", "trainer", "plan_group"], as_dict=True
        )
        if not plan or not plan.trainer:
            continue
        trainer = frappe.db.get_value(
            "Gym Trainer", plan.trainer,
            ["commission_percentage", "disabled"], as_dict=True
        )
        if not trainer or trainer.disabled or not trainer.commission_percentage:
            continue
        commission_amount = flt(item.amount) * flt(trainer.commission_percentage) / 100
        if commission_amount <= 0:
            continue
        try:
            frappe.get_doc({
                "doctype": "Gym Trainer Commission",
                "trainer": plan.trainer,
                "sales_invoice": doc.name,
                "member": doc.get("gym_member"),
                "gym_plan": plan.name,
                "sale_amount": item.amount,
                "commission_percentage": trainer.commission_percentage,
                "commission_amount": commission_amount,
                "date": nowdate(),
            }).insert(ignore_permissions=True)
            current_total = frappe.db.get_value("Gym Trainer", plan.trainer, "total_commission_earned") or 0
            frappe.db.set_value("Gym Trainer", plan.trainer, "total_commission_earned", flt(current_total) + commission_amount)
            frappe.db.commit()
        except Exception:
            frappe.log_error(title="Gym Trainer Commission Log Failed", message=frappe.get_traceback())
