import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        "Status:Data:150",
        "Count:Int:100",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select status, count(*) as count
        from `tabGym Subscription`
        where docstatus = 1
        group by status
        order by count desc
    """)
