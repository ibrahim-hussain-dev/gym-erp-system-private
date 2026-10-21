// Copyright (c) 2026, Noori and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gym Subscription", {
	refresh(frm) {
		// Freeze/Resume/Cancel is still managed only from the Gym Member form.
		if (!frm.is_new() && frm.doc.status === "Active") {
			frm.add_custom_button(__("Change Plan"), function () {
				open_change_plan_flow(frm.doc.name, frm.doc.gym_plan, function () {
					frm.reload_doc();
				});
			});
		}
	},
});

function open_change_plan_flow(subscription_name, current_plan, on_done) {
	let plan_dialog = new frappe.ui.Dialog({
		title: __("Change Plan"),
		fields: [
			{
				fieldname: "new_plan",
				fieldtype: "Link",
				options: "Gym Plan",
				label: __("New Plan"),
				reqd: 1,
				get_query: function () {
					return {
						filters: {
							name: ["!=", current_plan],
							disabled: 0,
							one_time_charge: 0,
						},
					};
				},
			},
			{
				fieldname: "mode",
				fieldtype: "Select",
				label: __("Activate New Plan For"),
				options: [
					{ label: __("Remaining Days Only (same end date as current plan)"), value: "remaining" },
					{ label: __("Full New Tenure (fresh full cycle from today)"), value: "full" },
				],
				reqd: 1,
				default: "remaining",
			},
		],
		primary_action_label: __("Calculate"),
		primary_action: function (values) {
			frappe.call({
				method: "gym_management.gym_erp_system.gym_subscription.preview_change_plan",
				args: { subscription: subscription_name, new_plan: values.new_plan },
				freeze: true,
				callback: function (r) {
					if (!r.message) return;
					plan_dialog.hide();
					show_change_plan_confirmation(subscription_name, values.new_plan, values.mode, r.message, on_done);
				},
			});
		},
	});
	plan_dialog.show();
}

function show_change_plan_confirmation(subscription_name, new_plan, mode, calc, on_done) {
	let chosen = calc.modes[mode];
	if (!chosen || !chosen.available) {
		frappe.msgprint(__("Is mode mein switch nahi ho sakta (remaining days 0 hain). Dusra mode try karein."));
		return;
	}
	let net = chosen.net_amount;
	let net_html;
	if (net > 0) {
		net_html =
			'<p style="font-size:16px;"><b>' +
			__("Customer has to pay") +
			": Rs " +
			frappe.format(net, { fieldtype: "Currency" }) +
			"</b></p>";
	} else if (net < 0) {
		net_html =
			'<p style="font-size:16px;"><b>' +
			__("You have to refund the customer") +
			": Rs " +
			frappe.format(Math.abs(net), { fieldtype: "Currency" }) +
			"</b></p>";
	} else {
		net_html =
			'<p style="font-size:16px;"><b>' + __("No payment or refund needed") + " (" + __("exact match") + ")</b></p>";
	}

	let summary_html =
		"<div>" +
		"<p><b>" +
		__("Current Plan") +
		":</b> " +
		calc.old_plan_label +
		" &mdash; " +
		__("remaining") +
		" " +
		calc.remaining_days +
		" " +
		__("day(s)") +
		", " +
		__("unused value") +
		": Rs " +
		frappe.format(calc.old_credit, { fieldtype: "Currency" }) +
		"</p>" +
		"<p><b>" +
		__("New Plan") +
		":</b> " +
		calc.new_plan_label +
		" &mdash; " +
		__("cost for this change") +
		": Rs " +
		frappe.format(chosen.new_cost, { fieldtype: "Currency" }) +
		", " +
		__("active until") +
		" " +
		frappe.datetime.str_to_user(chosen.new_end_date) +
		"</p>" +
		"<hr>" +
		net_html +
		"</div>";

	let confirm_dialog = new frappe.ui.Dialog({
		title: __("Confirm Plan Change"),
		fields: [{ fieldname: "summary", fieldtype: "HTML", options: summary_html }],
		primary_action_label: __("Confirm & Generate Bill"),
		primary_action: function () {
			frappe.call({
				method: "gym_management.gym_erp_system.gym_subscription.execute_change_plan",
				args: { subscription: subscription_name, new_plan: new_plan, mode: mode },
				freeze: true,
				freeze_message: __("Processing plan change..."),
				callback: function (r) {
					confirm_dialog.hide();
					if (!r.message) return;
					frappe.msgprint({
						title: __("Plan Changed"),
						message:
							__("New invoice {0} created.", [r.message.new_invoice]) +
							(r.message.credit_note ? " " + __("Credit note {0} created.", [r.message.credit_note]) : ""),
						indicator: "green",
					});
					if (on_done) on_done();
				},
			});
		},
	});
	confirm_dialog.show();
}
