import os
import random
import frappe
from frappe.utils import add_days, nowdate


def _cleanup_member(member_name):
    if not member_name:
        return
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
    frappe.delete_doc("Gym Member", member_name, force=True, ignore_permissions=True)
    if customer:
        try:
            frappe.delete_doc("Customer", customer, force=True, ignore_permissions=True)
        except Exception:
            pass


def run():
    results = []
    original_user = frappe.session.user
    test_member_name = None
    positive_member_name = None
    fd_user_email = "rbac.frontdesk.test@example.com"
    trainer_user_email = "rbac.trainer.test@example.com"

    try:
        from gym_management.gym_erp_system.api import sell_membership, record_expense
        from gym_management.gym_erp_system.gym_subscription import update_expired_subscriptions, run_daily_backup

        plan = frappe.db.get_value(
            "Gym Plan", {"disabled": 0, "one_time_charge": 0},
            ["name", "plan_name", "monthly_fee"], as_dict=True
        )

        # ---------- Test 1: Auto-Renew invoice due_date is today + 5 days ----------
        if not plan:
            results.append("SKIP: No active recurring Gym Plan found for due-date test.")
        else:
            suffix = random.randint(10000, 99999)
            sale = sell_membership(
                plans=[plan.name], is_new_member=1,
                full_name="DueDate Test Member", phone=f"032{suffix}",
                email=f"duedate.test.{suffix}@example.com",
            )
            test_member_name = sale["member"]
            test_sub_name = frappe.db.get_value("Gym Subscription", {"sales_invoice": sale["invoice"]}, "name")
            frappe.db.set_value("Gym Subscription", test_sub_name, "auto_renew", 1)
            frappe.db.set_value("Gym Subscription", test_sub_name, "end_date", add_days(nowdate(), -1))
            frappe.db.set_value("Gym Subscription", test_sub_name, "status", "Active")
            frappe.db.commit()
            update_expired_subscriptions()
            new_sub = frappe.db.get_value(
                "Gym Subscription", {"member": test_member_name, "status": "Active"},
                ["name", "sales_invoice"], as_dict=True
            )
            if new_sub:
                new_due_date = frappe.db.get_value("Sales Invoice", new_sub.sales_invoice, "due_date")
                expected_due = add_days(nowdate(), 5)
                if str(new_due_date) == str(expected_due):
                    results.append(f"PASS: Auto-renewed invoice due_date is {new_due_date} (today + 5 days)")
                else:
                    results.append(f"FAIL: Expected due_date {expected_due}, got {new_due_date}")
            else:
                results.append("FAIL: Auto-renew did not create a new Active subscription")

        # ---------- Set up temporary test staff accounts ----------
        for email, role in [(fd_user_email, "Gym Front Desk"), (trainer_user_email, "Gym Trainer")]:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True, ignore_permissions=True)
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": "RBAC Test",
                "roles": [{"role": role}],
            })
            user_doc.flags.no_welcome_mail = True
            user_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # ---------- Test 2: Trainer blocked from sell_membership ----------
        frappe.set_user(trainer_user_email)
        try:
            sell_membership(plans=[plan.name] if plan else [], member=test_member_name)
            results.append("FAIL: Trainer role was able to call sell_membership() - should have been blocked!")
        except frappe.PermissionError:
            results.append("PASS: Trainer role correctly BLOCKED from sell_membership()")
        except Exception as e:
            results.append(f"FAIL: sell_membership() raised unexpected error for Trainer: {e}")
        finally:
            frappe.set_user(original_user)

        # ---------- Test 3: Trainer blocked from record_expense ----------
        frappe.set_user(trainer_user_email)
        try:
            record_expense(expense_date=nowdate(), category="Test Category", amount=10)
            results.append("FAIL: Trainer role was able to call record_expense() - should have been blocked!")
        except frappe.PermissionError:
            results.append("PASS: Trainer role correctly BLOCKED from record_expense()")
        except Exception as e:
            results.append(f"FAIL: record_expense() raised unexpected error for Trainer: {e}")
        finally:
            frappe.set_user(original_user)

        # ---------- Test 4: Front Desk blocked from record_expense (Manager-only) ----------
        frappe.set_user(fd_user_email)
        try:
            record_expense(expense_date=nowdate(), category="Test Category", amount=10)
            results.append("FAIL: Front Desk role was able to call record_expense() - should have been blocked!")
        except frappe.PermissionError:
            results.append("PASS: Front Desk role correctly BLOCKED from record_expense() (Manager-only)")
        except Exception as e:
            results.append(f"FAIL: record_expense() raised unexpected error for Front Desk: {e}")
        finally:
            frappe.set_user(original_user)

        # ---------- Test 5: Front Desk CAN still complete a real sale (legitimate flow unaffected) ----------
        if plan:
            frappe.set_user(fd_user_email)
            try:
                suffix2 = random.randint(10000, 99999)
                sale2 = sell_membership(
                    plans=[plan.name], is_new_member=1,
                    full_name="FrontDesk Positive Test", phone=f"033{suffix2}",
                    email=f"frontdesk.positive.{suffix2}@example.com",
                )
                positive_member_name = sale2["member"]
                results.append("PASS: Front Desk role successfully completed a real sale (legitimate flow still works)")
            except Exception as e:
                results.append(f"FAIL: Front Desk role could not complete a legitimate sale: {e}")
            finally:
                frappe.set_user(original_user)

        # ---------- Test 6: Daily backup job creates a fresh backup file ----------
        backups_dir = frappe.get_site_path("private", "backups")
        before_files = set(os.listdir(backups_dir)) if os.path.isdir(backups_dir) else set()
        run_daily_backup()
        after_files = set(os.listdir(backups_dir)) if os.path.isdir(backups_dir) else set()
        new_files = after_files - before_files
        if any(f.endswith("-database.sql.gz") for f in new_files):
            results.append("PASS: run_daily_backup() created a new database backup file")
        else:
            results.append("FAIL: run_daily_backup() did not produce a new backup file")

        print("\n".join(results))
        if any(line.startswith("FAIL") for line in results):
            print("\nSOME TESTS FAILED - see above")
        else:
            print("\nALL TESTS PASSED")

    except Exception as e:
        results.append(f"FAIL (unexpected error): {str(e)}")
        print("\n".join(results))
        frappe.log_error(title="Security/Fixes Test Failed", message=frappe.get_traceback())
    finally:
        frappe.set_user(original_user)
        try:
            _cleanup_member(test_member_name)
            _cleanup_member(positive_member_name)
            for email in (fd_user_email, trainer_user_email):
                if frappe.db.exists("User", email):
                    frappe.delete_doc("User", email, force=True, ignore_permissions=True)
            frappe.db.commit()
            print("\nCleanup complete - all test users/members/invoices removed.")
        except Exception as cleanup_err:
            print(f"\nCLEANUP WARNING: {cleanup_err}")
