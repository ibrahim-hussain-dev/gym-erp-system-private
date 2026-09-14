import frappe
from frappe.utils import add_days, nowdate

def run():
    from gym_management.gym_erp_system.api import sell_membership
    from gym_management.gym_erp_system.gym_subscription import (
        freeze_subscription, resume_subscription, update_expired_subscriptions
    )

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
            full_name="NOTIFICATION TEST",
            phone="0000000000",
            email="pc16705.ibrahim@gmail.com",
            amount_received=0,
            auto_renew=1,
        )
        member = result["member"]
        invoice1 = result["invoice"]
        print("Step 1 - Member created:", member, "| Invoice:", invoice1, "-> Welcome email should be queued.")

        sub1 = frappe.db.get_value("Gym Subscription", {"sales_invoice": invoice1}, ["name"], as_dict=True)
        if not sub1:
            print("FAIL: No Gym Subscription created.")
            return

        freeze_subscription(sub1.name, 5)
        print("Step 2 - Subscription frozen:", sub1.name, "-> Freeze email should be queued.")

        resume_subscription(sub1.name)
        print("Step 2b - Subscription resumed back to Active.")

        frappe.db.set_value("Gym Subscription", sub1.name, "end_date", add_days(nowdate(), -1))
        frappe.db.commit()
        update_expired_subscriptions()
        print("Step 3 - Ran daily scheduler function -> Auto-Renew email should be queued (if renewal succeeded).")

        queued = frappe.get_all(
            "Email Queue",
            filters={"creation": [">", add_days(nowdate(), -1)]},
            fields=["name", "subject", "status"],
            order_by="creation desc",
            limit=10,
        )
        print("Recent Email Queue entries:")
        for q in queued:
            print(" -", q.subject, "|", q.status)

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
