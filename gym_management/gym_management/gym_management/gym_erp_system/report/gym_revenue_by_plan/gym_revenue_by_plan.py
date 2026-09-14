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
		{"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 130},
		{"label": "Plan", "fieldname": "plan_name", "fieldtype": "Data", "width": 180},
		{"label": "Total Sales", "fieldname": "line_items", "fieldtype": "Int", "width": 110},
		{"label": "Total Revenue", "fieldname": "total_revenue", "fieldtype": "Currency", "width": 150},
		{"label": "% of Total", "fieldname": "percent_of_total", "fieldtype": "Percent", "width": 100},
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

	if filters.get("plan"):
		conditions.append("gp.name = %(plan)s")
		values["plan"] = filters["plan"]

	return " and ".join(conditions), values


def get_data(filters):
	condition_str, values = get_conditions(filters)

	data = frappe.db.sql(f"""
		select
			coalesce(gm.branch, 'Unassigned') as branch,
			gp.plan_name,
			count(sii.name) as line_items,
			sum(sii.amount) as total_revenue
		from `tabSales Invoice Item` sii
		join `tabSales Invoice` si on si.name = sii.parent
		join `tabGym Plan` gp on gp.item = sii.item_code
		left join `tabGym Member` gm on gm.name = si.gym_member
		where {condition_str}
		group by branch, gp.plan_name
		order by total_revenue desc
	""", values, as_dict=True)

	grand_total = sum(flt(d.total_revenue) for d in data) or 1
	for d in data:
		d["percent_of_total"] = flt(d.total_revenue) / grand_total * 100

	return data


def get_chart(data):
	if not data:
		return None
	labels = [d.get("plan_name") for d in data]
	values = [flt(d.get("total_revenue")) for d in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Revenue", "values": values}]
		},
		"type": "bar",
		"colors": ["#0F9B8E"]
	}


def get_report_summary(data):
	total_revenue = sum(flt(d.get("total_revenue")) for d in data)
	total_lines = sum(d.get("line_items") or 0 for d in data)
	plan_count = len(set(d.get("plan_name") for d in data)) if data else 0
	avg_per_line = (total_revenue / total_lines) if total_lines else 0
	top_plan = max(data, key=lambda d: flt(d.get("total_revenue")))["plan_name"] if data else "-"

	return [
		{"value": total_revenue, "label": "Total Revenue", "datatype": "Currency", "indicator": "Green"},
		{"value": total_lines, "label": "Total Sales", "datatype": "Int", "indicator": "Blue"},
		{"value": avg_per_line, "label": "Avg Sale Value", "datatype": "Currency", "indicator": "Blue"},
		{"value": plan_count, "label": "Active Plans", "datatype": "Int", "indicator": "Orange"},
		{"value": top_plan, "label": "Top Plan", "datatype": "Data", "indicator": "Green"},
	]
