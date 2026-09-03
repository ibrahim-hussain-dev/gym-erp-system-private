import frappe
from frappe.utils import nowdate
from gym_management.gym_erp_system.notifications import send_noshow_email
def apply_session_deduction_from_attendance(attendance):
    slot_name = frappe.db.get_value(
        "Gym Slot",
        {"member": attendance.member, "date": attendance.date, "status": "Scheduled"},
        "name",
    )
    if not slot_name:
        return
    mark_slot_attended(slot_name)
def mark_slot_attended(slot_name):
    slot = frappe.get_doc("Gym Slot", slot_name)
    if slot.status != "Scheduled":
        return
    slot.status = "Attended"
    slot.flags.ignore_permissions = True
    slot.save()
    consume_session(slot.gym_subscription)
def consume_session(gym_subscription):
    if not gym_subscription:
        return
    sub = frappe.db.get_value("Gym Subscription", gym_subscription, ["sessions_used"], as_dict=True)
    if not sub:
        return
    frappe.db.set_value(
        "Gym Subscription", gym_subscription, "sessions_used", (sub.sessions_used or 0) + 1
    )
def mark_noshow_slots():
    """Daily job: any slot whose date has passed, still Scheduled (member never checked in,
    and trainer never cancelled), is marked No-show and the session is still consumed —
    the member's own absence does not entitle them to a free makeup session."""
    today = nowdate()
    pending = frappe.get_all(
        "Gym Slot",
        filters={"status": "Scheduled", "date": ["<", today]},
        fields=["name", "gym_subscription"],
    )
    for row in pending:
        frappe.db.set_value("Gym Slot", row.name, "status", "No-show")
        consume_session(row.gym_subscription)
        try:
            send_noshow_email(row.name)
        except Exception:
            frappe.log_error(title="Gym No-Show Email Failed", message=frappe.get_traceback())
    frappe.db.commit()
@frappe.whitelist()
def cancel_and_reschedule(slot, new_date, new_start_time=None, new_end_time=None):
    """Trainer-initiated cancellation: no session is consumed, and a fresh Scheduled
    slot is created on the make-up date."""
    old = frappe.get_doc("Gym Slot", slot)
    if old.status != "Scheduled":
        frappe.throw("Only a Scheduled slot can be cancelled/rescheduled.")
    old.status = "Cancelled by Trainer"
    old.flags.ignore_permissions = True
    old.save()
    new_slot = frappe.get_doc({
        "doctype": "Gym Slot",
        "member": old.member,
        "gym_subscription": old.gym_subscription,
        "trainer": old.trainer,
        "date": new_date,
        "start_time": new_start_time or old.start_time,
        "end_time": new_end_time or old.end_time,
        "status": "Scheduled",
        "rescheduled_from": old.name,
    })
    new_slot.flags.ignore_permissions = True
    new_slot.insert()
    return new_slot.name
