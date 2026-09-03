import frappe
from frappe.model.document import Document

COMPANY = "Gym ERP"


class GymExpense(Document):
    def on_submit(self):
        je = create_expense_journal_entry(self)
        self.db_set("journal_entry", je)

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            if je.docstatus == 1:
                je.flags.ignore_permissions = True
                je.cancel()


def create_expense_journal_entry(doc):
    expense_account = get_or_create_expense_account(doc.category)
    payment_account = get_payment_account(doc.payment_method)

    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = doc.expense_date
    je.company = COMPANY
    je.user_remark = "Gym Expense {0}: {1} - {2}".format(doc.name, doc.category, doc.paid_to or "")
    je.append("accounts", {
        "account": expense_account,
        "debit_in_account_currency": doc.amount,
        "credit_in_account_currency": 0,
    })
    je.append("accounts", {
        "account": payment_account,
        "debit_in_account_currency": 0,
        "credit_in_account_currency": doc.amount,
    })
    je.flags.ignore_permissions = True
    je.insert()
    je.submit()
    return je.name


def get_expense_parent_group():
    parent = frappe.db.get_value(
        "Account",
        {"company": COMPANY, "root_type": "Expense", "is_group": 1, "account_name": ["like", "%Indirect%"]},
        "name",
    )
    if not parent:
        parent = frappe.db.get_value(
            "Account", {"company": COMPANY, "root_type": "Expense", "is_group": 1}, "name", order_by="lft"
        )
    if not parent:
        frappe.throw(
            "No Expense account group found for company '{0}'. Please create one under "
            "Accounting > Chart of Accounts first.".format(COMPANY)
        )
    return parent


def get_or_create_expense_account(category):
    company = frappe.get_cached_doc("Company", COMPANY)
    account_name = "{0} - {1}".format(category, company.abbr)
    if frappe.db.exists("Account", account_name):
        return account_name
    acc = frappe.new_doc("Account")
    acc.account_name = category
    acc.company = COMPANY
    acc.parent_account = get_expense_parent_group()
    acc.root_type = "Expense"
    acc.report_type = "Profit and Loss"
    acc.is_group = 0
    acc.insert(ignore_permissions=True)
    return acc.name


def get_payment_account(payment_method):
    company = frappe.get_cached_doc("Company", COMPANY)
    if payment_method == "Bank":
        account = company.default_bank_account
    else:
        account = company.default_cash_account
    if not account:
        frappe.throw(
            "No Default {0} Account is set on Company '{1}'. Set one before recording expenses.".format(
                "Bank" if payment_method == "Bank" else "Cash", COMPANY
            )
        )
    return account
