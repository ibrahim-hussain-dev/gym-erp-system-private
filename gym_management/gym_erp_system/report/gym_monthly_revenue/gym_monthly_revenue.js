// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

frappe.query_reports["Gym Monthly Revenue"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Gym Branch"
		}
	]
};
