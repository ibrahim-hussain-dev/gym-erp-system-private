import frappe

# Order matters for the *cancel* step (financial documents must be cancelled
# in dependency order so ERPNext's own validation doesn't block it):
#   Payment Entry -> Sales Invoice (auto-cancels linked Gym Subscription via
#   the existing on_cancel hook) -> Gym Subscription (fallback, in case any
#   weren't auto-cancelled) -> Gym Expense (independent) -> everything else.
# Gym Timing Slot is intentionally excluded everywhere in this script.
CLEANUP_ORDER = [
    ("Payment Entry", "cancel financial docs first so invoice-cancel isn't blocked"),
    ("Sales Invoice", "cancelling also auto-cancels linked Gym Subscription via existing hook"),
    ("Gym Subscription", "fallback for any not auto-cancelled above"),
    ("Gym Expense", "independent submittable doc"),
    ("Gym Fitness Log", "draft records"),
    ("Gym Attendance", "draft records"),
    ("Gym Member", "after all documents referencing it are gone"),
    ("Gym Plan", "after all documents referencing it are gone"),
    ("Gym Package", "setup data being reset"),
    ("Gym Trainer", "setup data being reset"),
    ("Gym Branch", "setup data being reset"),
    ("Gym Trainer Availability", "setup data being reset"),
]

KEPT_INTENTIONALLY = ["Gym Timing Slot"]


def _cancel_and_delete(dt, note=""):
    if not frappe.db.exists("DocType", dt):
        print(f"--- {dt}: doctype does not exist, skipping ---")
        return []

    names = frappe.get_all(dt, pluck="name")
    print(f"--- {dt} ({note}): {len(names)} record(s) ---")

    cancelled = 0
    deleted = 0
    errors = []
    for name in names:
        try:
            doc = frappe.get_doc(dt, name)
            if doc.docstatus == 1:
                doc.cancel()
                cancelled += 1
        except Exception as e:
            errors.append((name, f"cancel failed: {e}"))
            continue
        try:
            frappe.delete_doc(dt, name, force=True, ignore_permissions=True, ignore_missing=True)
            deleted += 1
        except Exception as e:
            errors.append((name, f"delete failed: {e}"))

    print(f"  cancelled={cancelled} deleted={deleted} errors={len(errors)}")
    for name, err in errors:
        print(f"    FAILED {name}: {err}")
    return errors


def run():
    print("=" * 80)
    print("CLEANUP: wiping test/transactional data before client demo")
    print(f"KEPT INTENTIONALLY (never touched): {KEPT_INTENTIONALLY}")
    print("=" * 80)

    print()
    print("--- pre-flight counts ---")
    for dt, _ in CLEANUP_ORDER:
        if frappe.db.exists("DocType", dt):
            print(f"  {dt:25} total={frappe.db.count(dt)}")
    for dt in KEPT_INTENTIONALLY:
        print(f"  {dt:25} total={frappe.db.count(dt)}  (KEEPING)")

    all_errors = {}
    for dt, note in CLEANUP_ORDER:
        print()
        all_errors[dt] = _cancel_and_delete(dt, note)

    frappe.db.commit()

    print()
    print("=" * 80)
    print("VERIFICATION - remaining counts")
    print("=" * 80)
    for dt, _ in CLEANUP_ORDER:
        if frappe.db.exists("DocType", dt):
            print(f"  {dt:25} remaining={frappe.db.count(dt)}")
    for dt in KEPT_INTENTIONALLY:
        print(f"  {dt:25} remaining={frappe.db.count(dt)}  (kept intentionally)")

    print()
    total_errors = sum(len(v) for v in all_errors.values())
    if total_errors:
        print(f"WARNING: {total_errors} record(s) failed to clean up, see errors above.")
    else:
        print("DONE. All target records cleaned successfully.")
