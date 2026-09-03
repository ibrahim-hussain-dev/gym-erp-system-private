import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        "Branch:Data:130",
        "Plan:Data:180",
        "Invoice Lines:Int:110",
        "Total Revenue:Currency:150",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select
            coalesce(gm.branch, 'Unassigned') as branch,
            gp.plan_name,
            count(sii.name) as line_items,
            sum(sii.amount) as total_revenue
        from `tabSales Invoice Item` sii
        join `tabSales Invoice` si on si.name = sii.parent
        join `tabGym Plan` gp on gp.item = sii.item_code
        left join `tabGym Member` gm on gm.name = si.gym_member
        where si.docstatus = 1 and si.gym_member is not null and si.gym_member != ''
        group by branch, gp.plan_name
        order by branch, total_revenue desc
    """)
