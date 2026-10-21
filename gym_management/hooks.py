app_name = "gym_management"
app_title = "Gym Management"
app_publisher = "Frappe"
app_description = "Gym Management System"
app_email = "admin@example.com"
app_license = "mit"
app_include_css = "/assets/gym_management/css/gym_theme.css"
app_include_js = [
    "/assets/gym_management/js/gym_logout_override.js",
    "/assets/gym_management/js/gym_route_guard.js",
    "/assets/gym_management/js/gym_route_diag.js"
]
doc_events = {
    "Sales Invoice": {
        "validate": "gym_management.gym_erp_system.gym_subscription.apply_deferred_revenue",
        "on_submit": "gym_management.gym_erp_system.gym_subscription.create_subscription_from_invoice",
        "on_cancel": "gym_management.gym_erp_system.gym_subscription.cancel_from_invoice"
    },
    "Gym Member": {
        "after_insert": "gym_management.gym_erp_system.notifications.send_welcome_email"
    },
    "User": {
        "after_insert": "gym_management.gym_erp_system.user_setup.set_default_workspace_for_gym_user",
        "on_update": "gym_management.gym_erp_system.user_setup.set_default_workspace_for_gym_user"
    }
}
scheduler_events = {
    "daily": [
        "gym_management.gym_erp_system.gym_subscription.update_expired_subscriptions",
        "gym_management.gym_erp_system.gym_slot.mark_noshow_slots",
        "gym_management.gym_erp_system.notifications.send_expiry_reminders",
        "gym_management.gym_erp_system.notifications.send_invoice_due_reminders",
        "gym_management.gym_erp_system.gym_subscription.run_daily_backup"
    ]
}
# NOTE: Frappe's export_fixtures writes one file per entry, named only after
# the doctype (frappe.scrub(doctype) + ".json"), UNLESS a "prefix" is given.
# Two entries for the same doctype with no prefix silently overwrite each
# other on export -- only the LAST one survives in the file. Every doctype
# below that needs more than one filter condition either (a) is consolidated
# into a single entry using an "in" filter, or (b) gets a unique "prefix" so
# each entry writes to its own file. Verified empirically on 2026-10-21:
# without this, most Custom Field and all but one Client Script fixture were
# silently missing from every export.
fixtures = [
    {"doctype": "Custom Field", "prefix": "sales_invoice", "filters": [["dt", "=", "Sales Invoice"], ["fieldname", "=", "gym_member"]]},
    {"doctype": "Custom Field", "prefix": "sales_invoice_item", "filters": [["dt", "=", "Sales Invoice Item"], ["fieldname", "in", ["gym_package_duration_value", "gym_package_duration_unit"]]]},
    {"doctype": "Custom Field", "prefix": "gym_member", "filters": [["dt", "=", "Gym Member"], ["fieldname", "=", "branch"]]},
    {"doctype": "Custom Field", "prefix": "gym_trainer", "filters": [["dt", "=", "Gym Trainer"], ["fieldname", "in", ["commission_percentage", "total_commission_earned", "linked_user"]]]},  # fieldnames corrected 2026-10-21: DB has commission_percentage/total_commission_earned, NOT sessions_attended/total_commission (which never existed)
    {"doctype": "Custom Field", "prefix": "gym_package_item", "filters": [["dt", "=", "Gym Package Item"], ["fieldname", "=", "plan_price"]]},
    {"doctype": "Custom Field", "prefix": "gym_subscription", "filters": [["dt", "=", "Gym Subscription"], ["fieldname", "=", "auto_renew"]]},
    {"doctype": "Client Script", "filters": [["dt", "in", ["Gym Trainer", "Gym Member", "Gym Package"]]]},
    {"doctype": "Property Setter", "filters": [["doc_type", "in", ["Gym Package", "Gym Package Item"]]]},
    {"doctype": "Role", "filters": [["name", "in", ["Gym Front Desk", "Gym Trainer", "Gym Manager", "Gym Owner"]]]},
    {"doctype": "Custom DocPerm", "filters": [["role", "in", ["Gym Front Desk", "Gym Trainer", "Gym Manager", "Gym Owner"]]]},
    {"doctype": "Workspace", "filters": [["name", "in", ["Front Desk", "Impact Health Studio"]]]},
    {"doctype": "Workspace Sidebar", "filters": [["name", "in", ["Front Desk", "Impact Health Studio"]]]}
]
