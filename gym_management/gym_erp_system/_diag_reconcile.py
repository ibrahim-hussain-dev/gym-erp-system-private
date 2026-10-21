import frappe
from frappe.utils import flt

def dry_run(credit_note="ACC-SINV-2026-00110", new_invoice="ACC-SINV-2026-00111"):
    customer, company = frappe.db.get_value("Sales Invoice", new_invoice, ["customer", "company"])
    receivable_account = frappe.db.get_value("Company", company, "default_receivable_account")

    print("customer:", customer, "| company:", company, "| receivable_account:", receivable_account)

    pr = frappe.new_doc("Payment Reconciliation")
    pr.company = company
    pr.party_type = "Customer"
    pr.party = customer
    pr.receivable_payable_account = receivable_account
    pr.get_unreconciled_entries()

    print("===== PAYMENTS (incl dr/cr notes) =====")
    for p in pr.payments:
        print(dict(reference_type=p.reference_type, reference_name=p.reference_name,
                    reference_row=p.reference_row, amount=p.amount, currency=p.currency,
                    cost_center=p.cost_center, is_advance=p.is_advance, exchange_rate=p.exchange_rate))

    print("===== INVOICES =====")
    for i in pr.invoices:
        print(dict(invoice_type=i.invoice_type, invoice_number=i.invoice_number,
                    amount=i.amount, outstanding_amount=i.outstanding_amount,
                    currency=i.currency, exchange_rate=i.exchange_rate))

    match_p = [p for p in pr.payments if p.reference_name == credit_note]
    match_i = [i for i in pr.invoices if i.invoice_number == new_invoice]
    print("===== TARGET PAIR FOUND? =====")
    print("credit note row:", match_p[0].as_dict() if match_p else "NOT FOUND")
    print("new invoice row:", match_i[0].as_dict() if match_i else "NOT FOUND")
    # Nothing is saved, submitted, or committed in this function -- pure read.
