import time
import frappe


def _delete_user_with_retry(email, attempts=5):
    for i in range(attempts):
        try:
            if not frappe.db.exists("User", email):
                print(f"  {email}: already gone")
                return
            frappe.delete_doc("User", email, force=True, ignore_permissions=True)
            frappe.db.commit()
            print(f"  {email}: deleted successfully")
            return
        except Exception as e:
            frappe.db.rollback()
            print(f"  {email}: attempt {i+1} failed ({e}), retrying...")
            time.sleep(0.5)
    print(f"  {email}: FAILED after {attempts} attempts")


def run():
    for email in ("rbac.trainer.test@example.com", "rbac.frontdesk.test@example.com"):
        _delete_user_with_retry(email)

    remaining = frappe.get_all("User", filters={"email": ["like", "rbac.%"]}, fields=["email"])
    if remaining:
        print("\nSTILL REMAINING:", [u.email for u in remaining])
    else:
        print("\nCLEAN - all test users removed.")
