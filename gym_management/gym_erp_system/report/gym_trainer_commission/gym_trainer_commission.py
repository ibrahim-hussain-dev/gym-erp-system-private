import frappe


def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    chart = get_chart(data)
    report_summary = get_report_summary(data)
    return columns, data, None, chart, report_summary


def get_columns():
    return [
        {"label": "Trainer", "fieldname": "trainer_name", "fieldtype": "Data", "width": 160},
        {"label": "Commission %", "fieldname": "commission_percentage", "fieldtype": "Percent", "width": 110},
        {"label": "Active Plans", "fieldname": "active_plans", "fieldtype": "Int", "width": 100},
        {"label": "This Month", "fieldname": "this_month_commission", "fieldtype": "Currency", "width": 130},
        {"label": "Last Month", "fieldname": "last_month_commission", "fieldtype": "Currency", "width": 130},
        {"label": "Total Commission", "fieldname": "total_commission", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    # Sales-based figures: a single linear join chain (Gym Plan -> Sales Invoice Item ->
    # Sales Invoice), same shape as the already-verified total_commission formula, so
    # summing here cannot fan out / double-count. Deliberately kept separate from the
    # Gym Subscription count below (a second, unrelated join) to avoid a cartesian-product
    # bug that would corrupt both numbers if combined into one query.
    sales_rows = frappe.db.sql(
        """
        select
            gt.name as trainer,
            gt.trainer_name,
            gt.commission_percentage,
            coalesce(sum(case when si.name is not null then sii.amount else 0 end), 0) * gt.commission_percentage / 100 as total_commission,
            coalesce(sum(case
                when YEAR(si.posting_date) = YEAR(CURDATE()) and MONTH(si.posting_date) = MONTH(CURDATE())
                then sii.amount else 0 end), 0) * gt.commission_percentage / 100 as this_month_commission,
            coalesce(sum(case
                when YEAR(si.posting_date) = YEAR(CURDATE() - INTERVAL 1 MONTH)
                    and MONTH(si.posting_date) = MONTH(CURDATE() - INTERVAL 1 MONTH)
                then sii.amount else 0 end), 0) * gt.commission_percentage / 100 as last_month_commission
        from `tabGym Trainer` gt
        left join `tabGym Plan` gp on gp.trainer = gt.name
        left join `tabSales Invoice Item` sii on sii.item_code = gp.item
        left join `tabSales Invoice` si on si.name = sii.parent and si.docstatus = 1
        where gt.disabled = 0
        group by gt.name
        order by total_commission desc
        """,
        as_dict=True,
    )

    active_plan_counts = dict(
        frappe.db.sql(
            """
            select gp.trainer, count(*)
            from `tabGym Subscription` gs
            join `tabGym Plan` gp on gp.name = gs.gym_plan
            where gs.status = 'Active' and gp.trainer is not null
            group by gp.trainer
            """
        )
    )

    for row in sales_rows:
        row["active_plans"] = active_plan_counts.get(row["trainer"], 0)

    return sales_rows


def get_chart(data):
    if not data:
        return None
    return {
        "data": {
            "labels": [row["trainer_name"] for row in data],
            "datasets": [
                {"name": "This Month", "values": [row["this_month_commission"] for row in data]},
                {"name": "Last Month", "values": [row["last_month_commission"] for row in data]},
            ],
        },
        "type": "bar",
        "colors": ["#36A2EB", "#C7D3DD"],
    }


def get_report_summary(data):
    if not data:
        return None
    return [
        {
            "label": "This Month Commission",
            "value": sum(row["this_month_commission"] for row in data),
            "datatype": "Currency",
            "indicator": "Blue",
        },
        {
            "label": "Last Month Commission",
            "value": sum(row["last_month_commission"] for row in data),
            "datatype": "Currency",
            "indicator": "Blue",
        },
        {
            "label": "Active Plans (All Trainers)",
            "value": sum(row["active_plans"] for row in data),
            "datatype": "Int",
        },
    ]
