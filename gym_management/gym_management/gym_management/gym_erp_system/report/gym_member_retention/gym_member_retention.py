import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"label": "Member", "fieldname": "full_name", "fieldtype": "Data", "width": 160},
		{"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 110},
		{"label": "Plan", "fieldname": "gym_plan", "fieldtype": "Data", "width": 150},
		{"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 100},
		{"label": "Lapsed On", "fieldname": "end_date", "fieldtype": "Date", "width": 100},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": "Days Since Lapsed", "fieldname": "days_since_lapsed", "fieldtype": "Int", "width": 140},
		{"label": "Renewal Status", "fieldname": "renewal_status", "fieldtype": "Data", "width": 120},
	]


def get_conditions(filters):
	conditions = ["lsd.docstatus = 1", "lsd.status in ('Expired', 'Cancelled')"]
	values = {}

	if filters.get("from_date"):
		conditions.append("lsd.end_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("lsd.end_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	if filters.get("branch"):
		conditions.append("gm.branch = %(branch)s")
		values["branch"] = filters["branch"]

	if filters.get("plan"):
		conditions.append("lsd.gym_plan = %(plan)s")
		values["plan"] = filters["plan"]

	return " and ".join(conditions), values


def get_data(filters):
	condition_str, values = get_conditions(filters)

	data = frappe.db.sql(f"""
		with last_sub as (
			select member, max(end_date) as last_end_date
			from `tabGym Subscription`
			where docstatus = 1
			group by member
		)
		select
			gm.full_name,
			coalesce(gm.branch, 'Unassigned') as branch,
			lsd.gym_plan,
			lsd.start_date,
			lsd.end_date,
			lsd.status,
			datediff(curdate(), lsd.end_date) as days_since_lapsed,
			case when exists (
				select 1 from `tabGym Subscription` ns
				where ns.member = lsd.member and ns.docstatus = 1 and ns.start_date > lsd.end_date
			) then 'Renewed' else 'Churned' end as renewal_status
		from `tabGym Subscription` lsd
		join last_sub ls on ls.member = lsd.member and ls.last_end_date = lsd.end_date
		join `tabGym Member` gm on gm.name = lsd.member
		where {condition_str}
		order by lsd.end_date desc
	""", values, as_dict=True)

	return data


def get_chart(data):
	if not data:
		return None
	renewed = len([d for d in data if d.renewal_status == "Renewed"])
	churned = len([d for d in data if d.renewal_status == "Churned"])
	return {
		"data": {
			"labels": ["Renewed", "Churned"],
			"datasets": [{"name": "Members", "values": [renewed, churned]}]
		},
		"type": "bar",
		"colors": ["#0F9B8E", "#E4572E"]
	}


def get_report_summary(data):
	total = len(data)
	renewed = len([d for d in data if d.renewal_status == "Renewed"])
	churned = total - renewed
	retention_rate = (renewed / total * 100) if total else 0

	currently_active = frappe.db.count("Gym Subscription", {"status": "Active", "docstatus": 1})
	currently_frozen = frappe.db.count("Gym Subscription", {"status": "Frozen", "docstatus": 1})

	return [
		{"value": total, "label": "Lapsed Memberships", "datatype": "Int", "indicator": "Blue"},
		{"value": renewed, "label": "Renewed", "datatype": "Int", "indicator": "Green"},
		{"value": churned, "label": "Churned", "datatype": "Int", "indicator": "Red"},
		{"value": f"{retention_rate:.1f}%", "label": "Retention Rate", "datatype": "Data", "indicator": "Green" if retention_rate >= 50 else "Orange"},
		{"value": currently_active, "label": "Currently Active", "datatype": "Int", "indicator": "Green"},
		{"value": currently_frozen, "label": "Currently Frozen", "datatype": "Int", "indicator": "Blue"},
	]
