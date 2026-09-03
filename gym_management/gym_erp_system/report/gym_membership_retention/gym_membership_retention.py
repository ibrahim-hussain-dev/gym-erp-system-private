import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    total = sum(row[1] for row in data)
    churned = next((row[1] for row in data if row[0] == "Churned"), 0)
    rate = round((churned / total * 100), 1) if total else 0
    message = (
        "Churn Rate: {0}% ({1} of {2} members). "
        "'Churned' = most recent subscription expired 30+ days ago with no renewal. "
        "'Recently Expired (Grace)' = expired within the last 30 days."
    ).format(rate, churned, total)
    return columns, data, message

def get_columns():
    return [
        "Category:Data:220",
        "Member Count:Int:130",
    ]

def get_data(filters):
    return frappe.db.sql("""
        select
            case
                when active_subs > 0 then 'Active'
                when datediff(curdate(), latest_end) <= 30 then 'Recently Expired (Grace)'
                else 'Churned'
            end as category,
            count(*) as member_count
        from (
            select
                s.member,
                max(s.end_date) as latest_end,
                sum(case when s.status in ('Active','Scheduled','Frozen') then 1 else 0 end) as active_subs
            from `tabGym Subscription` s
            where s.docstatus = 1
            group by s.member
        ) t
        group by category
    """)
