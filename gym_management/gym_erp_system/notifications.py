import frappe
from frappe.utils import add_days, escape_html, nowdate


def get_member_email(member_name):
    return frappe.db.get_value("Gym Member", member_name, "email")


def get_member_full_name(member_name):
    return frappe.db.get_value("Gym Member", member_name, "full_name")


def _safe_full_name(member_name):
    name = get_member_full_name(member_name)
    return escape_html(name) if name else "Member"


def safe_send(recipient, subject, message):
    if not recipient:
        return
    try:
        frappe.sendmail(recipients=[recipient], subject=subject, message=message)
    except Exception:
        frappe.log_error(title="Gym Notification Email Failed", message=frappe.get_traceback())


def send_welcome_email(doc, method=None):
    if not doc.get("email"):
        return
    subject = "Welcome to the Gym Family!"
    full_name = escape_html(doc.full_name) if doc.full_name else "Member"
    message = """
        <p>Dear {full_name},</p>
        <p>Congratulations! You are now officially a member of our gym. We're excited to have you as part of our fitness family.</p>
        <p>Your Membership ID: <b>{member_id}</b></p>
        <p>If you have any questions, feel free to reach out to our front desk.</p>
        <p>See you at the gym!</p>
    """.format(full_name=full_name, member_id=doc.name)
    safe_send(doc.email, subject, message)


def send_freeze_email(subscription_name):
    sub = frappe.db.get_value(
        "Gym Subscription", subscription_name,
        ["member", "gym_plan", "freeze_start_date", "freeze_end_date"], as_dict=True
    )
    if not sub:
        return
    email = get_member_email(sub.member)
    full_name = _safe_full_name(sub.member)
    plan_name = frappe.db.get_value("Gym Plan", sub.gym_plan, "plan_name") or sub.gym_plan
    subject = "Your Membership Has Been Frozen"
    message = """
        <p>Dear {full_name},</p>
        <p>Your membership ({plan}) has been frozen from <b>{start}</b> to <b>{end}</b>.</p>
        <p>Your membership will automatically resume after this period, or you can ask the front desk to resume it earlier.</p>
    """.format(full_name=full_name, plan=plan_name, start=sub.freeze_start_date, end=sub.freeze_end_date)
    safe_send(email, subject, message)


def send_auto_renew_email(member, plan_name, new_invoice, new_end_date):
    email = get_member_email(member)
    full_name = _safe_full_name(member)
    subject = "Your Membership Has Been Auto-Renewed"
    message = """
        <p>Dear {full_name},</p>
        <p>Your membership ({plan}) has been automatically renewed.</p>
        <p>New Invoice: <b>{invoice}</b><br>Your membership is now valid until <b>{end_date}</b>.</p>
        <p>If you did not want this, please contact the front desk to disable Auto-Renew.</p>
    """.format(full_name=full_name, plan=plan_name, invoice=new_invoice, end_date=new_end_date)
    safe_send(email, subject, message)


def send_noshow_email(slot_name):
    slot = frappe.db.get_value(
        "Gym Slot", slot_name, ["member", "trainer", "date", "start_time"], as_dict=True
    )
    if not slot:
        return
    email = get_member_email(slot.member)
    full_name = _safe_full_name(slot.member)
    trainer_name = frappe.db.get_value("Gym Trainer", slot.trainer, "trainer_name") or slot.trainer
    subject = "You Missed Your PT Session"
    message = """
        <p>Dear {full_name},</p>
        <p>You had a Personal Training session scheduled on <b>{date}</b> at <b>{time}</b> with {trainer}, which you did not attend.</p>
        <p>This session has been deducted from your package as per policy. Please contact the front desk to book your next session.</p>
    """.format(full_name=full_name, date=slot.date, time=slot.start_time, trainer=trainer_name)
    safe_send(email, subject, message)


def send_expiry_reminders():
    """Daily job: email members whose Active membership expires in exactly 3 days."""
    target_date = add_days(nowdate(), 3)
    subs = frappe.get_all(
        "Gym Subscription",
        filters={"status": "Active", "end_date": target_date, "docstatus": 1},
        fields=["name", "member", "gym_plan", "end_date"],
    )
    for sub in subs:
        email = get_member_email(sub.member)
        full_name = _safe_full_name(sub.member)
        plan_name = frappe.db.get_value("Gym Plan", sub.gym_plan, "plan_name") or sub.gym_plan
        subject = "Your Membership is Expiring Soon"
        message = """
            <p>Dear {full_name},</p>
            <p>Your membership ({plan}) will expire on <b>{end_date}</b> (in 3 days).</p>
            <p>Please visit the front desk to renew your membership and continue enjoying uninterrupted access.</p>
        """.format(full_name=full_name, plan=plan_name, end_date=sub.end_date)
        safe_send(email, subject, message)


def send_invoice_due_reminders():
    """Daily job: email members whose Sales Invoice due date is today and still has an outstanding amount."""
    today = nowdate()
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "due_date": today,
            "outstanding_amount": [">", 0],
            "gym_member": ["is", "set"],
        },
        fields=["name", "gym_member", "outstanding_amount", "due_date"],
    )
    for inv in invoices:
        email = get_member_email(inv.gym_member)
        full_name = _safe_full_name(inv.gym_member)
        subject = "Payment Due Today"
        message = """
            <p>Dear {full_name},</p>
            <p>This is a reminder that your invoice <b>{invoice}</b> with an outstanding amount of <b>Rs {amount}</b> is due today ({due_date}).</p>
            <p>Please clear this at your earliest convenience at the front desk.</p>
        """.format(full_name=full_name, invoice=inv.name, amount=inv.outstanding_amount, due_date=inv.due_date)
        safe_send(email, subject, message)
