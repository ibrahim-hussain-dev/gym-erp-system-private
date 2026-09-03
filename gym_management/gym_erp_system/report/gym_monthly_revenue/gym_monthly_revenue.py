import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        "Month:Data:120",
        "Invoices:Int:100",
        "Total Revenue:Currency:150",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select
            date_format(posting_date, '%Y-%m') as month,
            count(*) as invoices,
            sum(grand_total) as total_revenue
        from `tabSales Invoice`
        where docstatus = 1 and gym_member is not null and gym_member != ''
        group by date_format(posting_date, '%Y-%m')
        order by month desc
    """)
