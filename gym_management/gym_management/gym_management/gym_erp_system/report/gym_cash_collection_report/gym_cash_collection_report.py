import frappe
from frappe.utils import flt, nowdate

def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or nowdate()
    to_date = filters.get("to_date") or nowdate()

    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Data", "width": 160},
        {"label": "Invoices Raised (Accrual)", "fieldname": "invoiced_amount", "fieldtype": "Currency", "width": 190},
        {"label": "Cash/Bank Collected (Cash Basis Sale)", "fieldname": "collected_amount", "fieldtype": "Currency", "width": 220},
        {"label": "New Receivable Added", "fieldname": "receivable_added", "fieldtype": "Currency", "width": 180},
    ]

    invoiced = frappe.db.sql("""
        select posting_date as date, sum(grand_total) as amount
        from `tabSales Invoice`
        where docstatus = 1 and company = %s and posting_date between %s and %s
        group by posting_date
    """, ("Gym ERP", from_date, to_date), as_dict=True)

    collected = frappe.db.sql("""
        select posting_date as date, sum(paid_amount) as amount
        from `tabPayment Entry`
        where docstatus = 1 and payment_type = 'Receive' and company = %s and posting_date between %s and %s
        group by posting_date
    """, ("Gym ERP", from_date, to_date), as_dict=True)

    invoiced_map = {str(r.date): flt(r.amount) for r in invoiced}
    collected_map = {str(r.date): flt(r.amount) for r in collected}
    all_dates = sorted(set(list(invoiced_map.keys()) + list(collected_map.keys())))

    data = []
    for d in all_dates:
        inv_amt = invoiced_map.get(d, 0)
        coll_amt = collected_map.get(d, 0)
        data.append({
            "date": d,
            "invoiced_amount": inv_amt,
            "collected_amount": coll_amt,
            "receivable_added": inv_amt - coll_amt,
        })

    total_outstanding = frappe.db.sql("""
        select sum(outstanding_amount) from `tabSales Invoice`
        where docstatus = 1 and company = %s
    """, ("Gym ERP",))[0][0] or 0

    data.append({
        "date": "PERIOD TOTAL",
        "invoiced_amount": sum(invoiced_map.values()),
        "collected_amount": sum(collected_map.values()),
        "receivable_added": sum(invoiced_map.values()) - sum(collected_map.values()),
    })
    data.append({
        "date": "TOTAL OUTSTANDING RECEIVABLES (ALL TIME)",
        "invoiced_amount": None,
        "collected_amount": None,
        "receivable_added": flt(total_outstanding),
    })

    return columns, data
