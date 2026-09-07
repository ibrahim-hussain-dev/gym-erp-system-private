import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 100},
		{"label": "Invoices", "fieldname": "invoices", "fieldtype": "Int", "width": 90},
		{"label": "Active Members", "fieldname": "active_members", "fieldtype": "Int", "width": 130},
		{"label": "New Members", "fieldname": "new_members", "fieldtype": "Int", "width": 120},
		{"label": "Total Revenue", "fieldname": "total_revenue", "fieldtype": "Currency", "width": 140},
		{"label": "Avg / Invoice", "fieldname": "avg_per_invoice", "fieldtype": "Currency", "width": 120},
		{"label": "MoM Growth", "fieldname": "mom_growth", "fieldtype": "Percent", "width": 110},
	]


def get_conditions(filters):
	conditions = ["si.docstatus = 1", "si.gym_member is not null", "si.gym_member != ''"]
	values = {}

	if filters.get("from_date"):
		conditions.append("si.posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("si.posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	if filters.get("branch"):
		conditions.append("gm.branch = %(branch)s")
		values["branch"] = filters["branch"]

	return " and ".join(conditions), values


def get_data(filters):
	condition_str, values = get_conditions(filters)

	data = frappe.db.sql(f"""
		with first_purchase as (
			select gym_member, min(posting_date) as first_date
			from `tabSales Invoice`
			where docstatus = 1 and gym_member is not null and gym_member != ''
			group by gym_member
		)
		select
			date_format(si.posting_date, '%%Y-%%m') as month,
			count(*) as invoices,
			count(distinct si.gym_member) as active_members,
			count(distinct case when date_format(fp.first_date, '%%Y-%%m') = date_format(si.posting_date, '%%Y-%%m') then si.gym_member end) as new_members,
			sum(si.grand_total) as total_revenue
		from `tabSales Invoice` si
		left join `tabGym Member` gm on gm.name = si.gym_member
		left join first_purchase fp on fp.gym_member = si.gym_member
		where {condition_str}
		group by date_format(si.posting_date, '%%Y-%%m')
		order by month desc
	""", values, as_dict=True)

	for d in data:
		d["avg_per_invoice"] = flt(d.total_revenue) / d.invoices if d.invoices else 0

	for i, d in enumerate(data):
		if i + 1 < len(data):
			prev = flt(data[i + 1].total_revenue)
			d["mom_growth"] = ((flt(d.total_revenue) - prev) / prev * 100) if prev else None
		else:
			d["mom_growth"] = None

	return data


def get_chart(data):
	if not data:
		return None
	ordered = list(reversed(data))
	labels = [d.get("month") for d in ordered]
	values = [flt(d.get("total_revenue")) for d in ordered]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Revenue", "values": values}]
		},
		"type": "line",
		"colors": ["#0F9B8E"]
	}


def get_report_summary(data):
	total_revenue = sum(flt(d.get("total_revenue")) for d in data)
	total_invoices = sum(d.get("invoices") or 0 for d in data)
	total_new_members = sum(d.get("new_members") or 0 for d in data)
	month_count = len(data) or 1
	avg_per_month = total_revenue / month_count
	growth = data[0].get("mom_growth") if data else None
	best_month = max(data, key=lambda d: flt(d.get("total_revenue")))["month"] if data else "-"

	summary = [
		{"value": total_revenue, "label": "Total Revenue", "datatype": "Currency", "indicator": "Green"},
		{"value": total_invoices, "label": "Total Invoices", "datatype": "Int", "indicator": "Blue"},
		{"value": total_new_members, "label": "New Members", "datatype": "Int", "indicator": "Blue"},
		{"value": avg_per_month, "label": "Avg Revenue / Month", "datatype": "Currency", "indicator": "Blue"},
		{"value": best_month, "label": "Best Month", "datatype": "Data", "indicator": "Green"},
	]

	if growth is not None:
		summary.append({
			"value": f"{growth:.1f}%",
			"label": "Latest MoM Growth",
			"datatype": "Data",
			"indicator": "Green" if growth >= 0 else "Red"
		})

	return summary
