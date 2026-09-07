app_name = "gym_management"
app_title = "Gym Management"
app_publisher = "Frappe"
app_description = "Gym Management System"
app_email = "admin@example.com"
app_license = "mit"
app_include_css = "/assets/gym_management/css/gym_theme.css"
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
fixtures = [
    {"doctype": "Custom Field", "filters": [["dt", "=", "Sales Invoice"], ["fieldname", "=", "gym_member"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Sales Invoice Item"], ["fieldname", "in", ["gym_package_duration_value", "gym_package_duration_unit"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Member"], ["fieldname", "=", "branch"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Trainer"], ["fieldname", "in", ["sessions_attended", "total_commission"]]]},
    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Trainer"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Package Item"], ["fieldname", "=", "plan_price"]]},
    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Package"]]},
    {"doctype": "Property Setter", "filters": [["doc_type", "in", ["Gym Package", "Gym Package Item"]]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Subscription"], ["fieldname", "=", "auto_renew"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Promo Code"], ["fieldname", "=", "times_used"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Sales Invoice"], ["fieldname", "=", "promo_code"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Trainer"], ["fieldname", "=", "linked_user"]]},
    {"doctype": "Role", "filters": [["name", "in", ["Gym Front Desk", "Gym Trainer", "Gym Manager"]]]},
    {"doctype": "Custom DocPerm", "filters": [["role", "in", ["Gym Front Desk", "Gym Trainer", "Gym Manager"]]]}
]
