// Copyright (c) 2026, Noori and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gym Subscription", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) {
            return;
        }

        if (frm.doc.status === "Active") {
            frm.add_custom_button("Freeze", () => {
                frappe.prompt(
                    [
                        {
                            fieldname: "freeze_days",
                            fieldtype: "Int",
                            label: "Freeze Duration (Days)",
                            reqd: 1,
                        },
                    ],
                    (values) => {
                        frappe.call({
                            method: "gym_management.gym_erp_system.gym_subscription.freeze_subscription",
                            args: {
                                subscription: frm.doc.name,
                                freeze_days: values.freeze_days,
                            },
                            freeze: true,
                            freeze_message: "Freezing subscription...",
                            callback: () => {
                                frappe.show_alert({ message: "Subscription frozen.", indicator: "green" });
                                frm.reload_doc();
                            },
                        });
                    },
                    "Freeze Subscription",
                    "Freeze"
                );
            });

            frm.add_custom_button("Cancel Subscription", () => {
                frappe.prompt(
                    [
                        {
                            fieldname: "reason",
                            fieldtype: "Small Text",
                            label: "Cancellation Reason",
                        },
                    ],
                    (values) => {
                        frappe.confirm(
                            "Are you sure you want to cancel this subscription? This cannot be undone.",
                            () => {
                                frappe.call({
                                    method: "gym_management.gym_erp_system.gym_subscription.cancel_subscription",
                                    args: {
                                        subscription: frm.doc.name,
                                        reason: values.reason,
                                    },
                                    freeze: true,
                                    freeze_message: "Cancelling subscription...",
                                    callback: () => {
                                        frappe.show_alert({ message: "Subscription cancelled.", indicator: "orange" });
                                        frm.reload_doc();
                                    },
                                });
                            }
                        );
                    },
                    "Cancel Subscription",
                    "Cancel"
                );
            });
        }

        if (frm.doc.status === "Frozen") {
            frm.add_custom_button("Resume", () => {
                frappe.call({
                    method: "gym_management.gym_erp_system.gym_subscription.resume_subscription",
                    args: { subscription: frm.doc.name },
                    freeze: true,
                    freeze_message: "Resuming subscription...",
                    callback: () => {
                        frappe.show_alert({ message: "Subscription resumed.", indicator: "green" });
                        frm.reload_doc();
                    },
                });
            });
        }
    },
});
