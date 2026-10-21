import random
import frappe


def run():
    original_user = frappe.session.user
    fd_user_email = "rbac.frontdesk.diag@example.com"
    member_name = None

    try:
        if frappe.db.exists("User", fd_user_email):
            frappe.delete_doc("User", fd_user_email, force=True, ignore_permissions=True)
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": fd_user_email,
            "first_name": "RBAC Diag",
            "roles": [{"role": "Gym Front Desk"}],
        })
        user_doc.flags.no_welcome_mail = True
        user_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        from gym_management.gym_erp_system.api import sell_membership
        plan = frappe.db.get_value(
            "Gym Plan", {"disabled": 0, "one_time_charge": 0},
            ["name", "plan_name", "monthly_fee"], as_dict=True
        )
        print("=== Test: Front Desk sale ===")
        frappe.set_user(fd_user_email)
        suffix = random.randint(10000, 99999)
        try:
            sale = sell_membership(
                plans=[plan.name], is_new_member=1,
                full_name="Diag Positive Test", phone=f"034{suffix}",
                email=f"diag.positive.{suffix}@example.com",
            )
            member_name = sale["member"]
            print("SALE SUCCEEDED:", sale)
        except Exception:
            print("SALE FAILED - FULL TRACEBACK:")
            print(frappe.get_traceback())
        finally:
            frappe.set_user(original_user)

        print("\n=== Test: Direct backup attempt (bypassing the safety try/except) ===")
        try:
            from frappe.utils.backups import new_backup
            backup_obj = new_backup(ignore_files=False)
            print("BACKUP SUCCEEDED:", backup_obj)
        except Exception:
            print("BACKUP FAILED - FULL TRACEBACK:")
            print(frappe.get_traceback())

    finally:
        frappe.set_user(original_user)
        try:
            if member_name:
                customer = frappe.db.get_value("Gym Member", member_name, "customer")
                for sub in frappe.get_all("Gym Subscription", filters={"member": member_name}):
                    subdoc = frappe.get_doc("Gym Subscription", sub.name)
                    if subdoc.docstatus == 1:
                        subdoc.cancel()
                    frappe.delete_doc("Gym Subscription", sub.name, force=True, ignore_permissions=True)
                for inv in frappe.get_all("Sales Invoice", filters={"gym_member": member_name}):
                    invdoc = frappe.get_doc("Sales Invoice", inv.name)
                    if invdoc.docstatus == 1:
                        invdoc.cancel()
                    frappe.delete_doc("Sales Invoice", inv.name, force=True, ignore_permissions=True)
                frappe.db.commit()
                frappe.delete_doc("Gym Member", member_name, force=True, ignore_permissions=True)
                if customer:
                    try:
                        frappe.delete_doc("Customer", customer, force=True, ignore_permissions=True)
                    except Exception:
                        pass
            if frappe.db.exists("User", fd_user_email):
                frappe.delete_doc("User", fd_user_email, force=True, ignore_permissions=True)
            frappe.db.commit()
            print("\nCleanup complete.")
        except Exception as cleanup_err:
            print(f"\nCLEANUP WARNING: {cleanup_err}")
