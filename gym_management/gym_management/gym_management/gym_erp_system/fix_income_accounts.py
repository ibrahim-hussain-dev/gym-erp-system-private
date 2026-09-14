import frappe
from frappe.model.naming import make_autoname


def run():
    from gym_management.gym_erp_system.doctype.gym_plan.gym_plan import get_default_income_account

    income_account = get_default_income_account()
    plans = frappe.get_all(
        "Gym Plan",
        filters={"item": ["in", ["", None]]},
        fields=["name", "plan_name", "monthly_fee"],
    )

    created = []
    for plan in plans:
        item = frappe.new_doc("Item")
        item.item_code = make_autoname("ITEM-.YYYY.-.#####")
        item.item_name = plan.plan_name or plan.name
        item.item_group = "Services"
        item.is_stock_item = 0
        item.is_sales_item = 1
        item.include_item_in_manufacturing = 0
        item.stock_uom = "Nos"
        item.standard_rate = plan.monthly_fee or 0
        item.append("item_defaults", {"company": "Gym ERP", "income_account": income_account})
        item.insert(ignore_permissions=True)

        frappe.db.set_value("Gym Plan", plan.name, "item", item.name)
        created.append((plan.name, item.name))

    frappe.db.commit()
    print("Income account used:", income_account)
    print("Items created for plans:", created)
