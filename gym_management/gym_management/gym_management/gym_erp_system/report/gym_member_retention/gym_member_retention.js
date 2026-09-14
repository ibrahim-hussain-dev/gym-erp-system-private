// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

frappe.query_reports["Gym Member Retention"] = {
	filters: [
		{ fieldname: "from_date", label: __("Lapsed From"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("Lapsed To"), fieldtype: "Date" },
		{ fieldname: "branch", label: __("Branch"), fieldtype: "Link", options: "Gym Branch" },
		{ fieldname: "plan", label: __("Plan"), fieldtype: "Link", options: "Gym Plan" },
	]
};
