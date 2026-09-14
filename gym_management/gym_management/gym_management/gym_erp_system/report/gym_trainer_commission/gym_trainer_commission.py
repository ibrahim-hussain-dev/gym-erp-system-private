import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        "Trainer:Data:180",
        "Commission %:Percent:110",
        "Total Commission Earned:Currency:180",
        "Sales Logged:Int:120",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select
            gt.trainer_name,
            gt.commission_percentage,
            gt.total_commission_earned,
            count(gtc.name) as sales_logged
        from `tabGym Trainer` gt
        left join `tabGym Trainer Commission` gtc on gtc.trainer = gt.name
        where gt.disabled = 0
        group by gt.name
        order by gt.total_commission_earned desc
    """, as_dict=True)
