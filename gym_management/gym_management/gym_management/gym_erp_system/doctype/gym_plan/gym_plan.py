import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

COMPANY = "Gym ERP"


def get_default_income_account():
    income_account = frappe.db.get_value(
        "Item Default", {"parent": "Services", "company": COMPANY}, "income_account"
    )
    if income_account:
        return income_account

    income_account = frappe.db.get_value("Company", COMPANY, "default_income_account")
    if income_account:
        return income_account

    frappe.throw(
        "No default Income Account configured for company '{0}'. "
        "Set one on Company > {0} > Default Income Account, "
        "or on Item Group > Services > Item Defaults.".format(COMPANY)
    )


class GymPlan(Document):
    def before_insert(self):
        if self.item:
            return

        item = frappe.new_doc("Item")
        item.item_code = make_autoname("ITEM-.YYYY.-.#####")
        item.item_name = self.plan_name
        item.item_group = "Services"
        item.is_stock_item = 0
        item.is_sales_item = 1
        item.include_item_in_manufacturing = 0
        item.stock_uom = "Nos"
        item.standard_rate = self.monthly_fee
        item.append("item_defaults", {
            "company": COMPANY,
            "income_account": get_default_income_account(),
        })
        item.insert(ignore_permissions=True)
        self.item = item.name

    def on_update(self):
        if self.item and self.has_value_changed("monthly_fee"):
            frappe.db.set_value("Item", self.item, "standard_rate", self.monthly_fee)
        if self.item and self.has_value_changed("disabled"):
            frappe.db.set_value("Item", self.item, "disabled", self.disabled)
