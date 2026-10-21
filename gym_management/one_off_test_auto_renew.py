import frappe
from frappe.utils import add_days, nowdate

def run():
    from gym_management.gym_erp_system.api import sell_membership
    from gym_management.gym_erp_system.gym_subscription import update_expired_subscriptions

    plan = frappe.db.get_value(
        "Gym Plan", {"one_time_charge": 0, "disabled": 0}, ["name", "plan_name"], as_dict=True
    )
    if not plan:
        print("FAIL: No active recurring Gym Plan found to test with.")
        return

    print("Using test plan:", plan.plan_name)
    member = None

    try:
        result = sell_membership(
            plans=[plan.name],
            member=None,
            is_new_member=1,
            full_name="AUTO RENEW TEST",
            phone="0000000000",
            email="autorenewtest@example.com",
            amount_received=0,
            auto_renew=1,
        )
        member = result["member"]
        invoice1 = result["invoice"]
        print("Created test member:", member, "| Invoice 1:", invoice1)

        sub1 = frappe.db.get_value(
            "Gym Subscription", {"sales_invoice": invoice1},
            ["name", "auto_renew", "end_date"], as_dict=True
        )
        if not sub1:
            print("FAIL: No Gym Subscription was created from the test invoice.")
            return
        print("Subscription 1:", sub1.name, "| auto_renew:", sub1.auto_renew, "| end_date:", sub1.end_date)

        frappe.db.set_value("Gym Subscription", sub1.name, "end_date", add_days(nowdate(), -1))
        frappe.db.commit()

        update_expired_subscriptions()

        sub1_status = frappe.db.get_value("Gym Subscription", sub1.name, "status")
        print("Subscription 1 status after scheduler run:", sub1_status)

        new_sub = frappe.db.get_value(
            "Gym Subscription",
            {"member": member, "name": ["!=", sub1.name]},
            ["name", "sales_invoice", "status", "start_date", "end_date"],
            as_dict=True, order_by="creation desc",
        )

        if sub1_status == "Expired" and new_sub:
            print("PASS: Auto-Renew worked.")
            print("  New Sales Invoice:", new_sub.sales_invoice)
            print("  New Subscription:", new_sub.name, "| Status:", new_sub.status, "| Start:", new_sub.start_date, "| End:", new_sub.end_date)
        else:
            print("FAIL: Auto-Renew did not create a new subscription.")

    finally:
        if member:
            print("Cleaning up test data...")
            for inv_name in frappe.get_all("Sales Invoice", filters={"gym_member": member}, pluck="name"):
                inv_doc = frappe.get_doc("Sales Invoice", inv_name)
                if inv_doc.docstatus == 1:
                    inv_doc.flags.ignore_permissions = True
                    inv_doc.cancel()
            for sub_name in frappe.get_all("Gym Subscription", filters={"member": member}, pluck="name"):
                frappe.delete_doc("Gym Subscription", sub_name, force=True, ignore_permissions=True)
            for inv_name in frappe.get_all("Sales Invoice", filters={"gym_member": member}, pluck="name"):
                frappe.delete_doc("Sales Invoice", inv_name, force=True, ignore_permissions=True)
            customer = frappe.db.get_value("Gym Member", member, "customer")
            frappe.delete_doc("Gym Member", member, force=True, ignore_permissions=True)
            if customer:
                try:
                    frappe.delete_doc("Customer", customer, force=True, ignore_permissions=True)
                except Exception:
                    pass
            frappe.db.commit()
            print("Cleanup done. No test data left behind.")
