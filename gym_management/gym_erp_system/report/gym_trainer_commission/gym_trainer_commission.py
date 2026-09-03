import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        "Trainer:Data:180",
        "Price / Session:Currency:120",
        "Sessions Attended:Int:150",
        "Total Commission:Currency:150",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select
            gt.trainer_name,
            gt.price_per_session,
            count(gs.name) as sessions_attended,
            (count(gs.name) * gt.price_per_session) as total_commission
        from `tabGym Trainer` gt
        left join `tabGym Slot` gs on gs.trainer = gt.name and gs.status = 'Attended'
        where gt.disabled = 0
        group by gt.name
        order by total_commission desc
    """)
