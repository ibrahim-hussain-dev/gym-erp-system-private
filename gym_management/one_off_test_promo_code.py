import random
import frappe
from frappe.utils import add_days, flt, nowdate


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
    member_name = None
    member_name_2 = None
    promo_code = "TESTPROMO10"
    expired_code = "TESTEXPIRED10"

    try:
        from gym_management.gym_erp_system.api import sell_membership, validate_promo_code

        plan = frappe.db.get_value(
            "Gym Plan", {"disabled": 0, "one_time_charge": 0},
            ["name", "plan_name", "monthly_fee"], as_dict=True
        )
        if not plan:
            print("FAIL: No active recurring Gym Plan found to test with. Create one and re-run.")
            return
        results.append(f"Using existing plan: {plan.plan_name} (Rs {plan.monthly_fee})")

        for code in (promo_code, expired_code):
            if frappe.db.exists("Gym Promo Code", code):
                frappe.delete_doc("Gym Promo Code", code, force=True, ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Gym Promo Code",
            "promo_code": promo_code,
            "discount_percentage": 10,
            "is_active": 1,
            "max_usage": 1,
            "single_use_per_member": 1,
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        results.append("Created test Promo Code: TESTPROMO10 (10% off, max_usage=1)")

        r = validate_promo_code(promo_code)
        assert r["valid"] and flt(r["discount_percentage"]) == 10, f"Expected valid 10% discount, got {r}"
        results.append("PASS: validate_promo_code() returns valid=True, 10% discount")

        r_bad = validate_promo_code("NONEXISTENT_CODE_XYZ")
        assert r_bad["valid"] is False, f"Expected invalid, got {r_bad}"
        results.append("PASS: validate_promo_code() correctly rejects a nonexistent code")

        frappe.get_doc({
            "doctype": "Gym Promo Code",
            "promo_code": expired_code,
            "discount_percentage": 20,
            "is_active": 1,
            "valid_till": add_days(nowdate(), -1),
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        r_exp = validate_promo_code(expired_code)
        assert r_exp["valid"] is False, f"Expected expired code invalid, got {r_exp}"
        results.append("PASS: validate_promo_code() correctly rejects an expired code")
        frappe.delete_doc("Gym Promo Code", expired_code, force=True, ignore_permissions=True)
        frappe.db.commit()

        suffix = random.randint(10000, 99999)
        sale = sell_membership(
            plans=[plan.name],
            is_new_member=1,
            full_name="Promo Test Member",
            phone=f"030{suffix}",
            email=f"promo.test.{suffix}@example.com",
            promo_code=promo_code,
        )
        member_name = sale["member"]
        invoice_name = sale["invoice"]
        results.append(f"Created test member {member_name}, invoice {invoice_name}, grand_total Rs {sale['grand_total']}")

        expected_total = flt(plan.monthly_fee) * 0.9
        actual_total = flt(sale["grand_total"])
        assert abs(actual_total - expected_total) < 1, f"Expected ~{expected_total}, got {actual_total}"
        results.append(f"PASS: Invoice grand_total ({actual_total}) reflects the 10% discount (expected ~{expected_total})")

        times_used = frappe.db.get_value("Gym Promo Code", promo_code, "times_used")
        assert times_used == 1, f"Expected times_used=1, got {times_used}"
        results.append("PASS: Promo Code times_used incremented to 1")

        stored_promo = frappe.db.get_value("Sales Invoice", invoice_name, "promo_code")
        assert stored_promo == promo_code, f"Expected promo_code stored on invoice, got {stored_promo}"
        results.append("PASS: Sales Invoice.promo_code field correctly stored")

        suffix2 = random.randint(10000, 99999)
        try:
            sale2 = sell_membership(
                plans=[plan.name],
                is_new_member=1,
                full_name="Promo Test Member 2",
                phone=f"031{suffix2}",
                email=f"promo.test2.{suffix2}@example.com",
                promo_code=promo_code,
            )
            member_name_2 = sale2.get("member")
            results.append("FAIL: A second use of a max_usage=1 promo code should have been blocked but wasn't!")
        except Exception as e:
            results.append(f"PASS: Second use of the promo code was correctly blocked ({str(e)})")

        print("\n".join(results))
        if any(line.startswith("FAIL") for line in results):
            print("\nSOME PROMO CODE TESTS FAILED — see above")
        else:
            print("\nALL PROMO CODE TESTS PASSED")

    except AssertionError as e:
        results.append(f"FAIL: {str(e)}")
        print("\n".join(results))
    except Exception as e:
        results.append(f"FAIL (unexpected error): {str(e)}")
        print("\n".join(results))
        frappe.log_error(title="Promo Code Test Failed", message=frappe.get_traceback())
    finally:
        try:
            _cleanup_member(member_name)
            _cleanup_member(member_name_2)
            for code in (promo_code, expired_code):
                if frappe.db.exists("Gym Promo Code", code):
                    frappe.delete_doc("Gym Promo Code", code, force=True, ignore_permissions=True)
            frappe.db.commit()
            print("\nCleanup complete — all test data removed.")
        except Exception as cleanup_err:
            print(f"\nCLEANUP WARNING: {cleanup_err}")
