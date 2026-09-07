import frappe
from frappe.utils import add_days, add_months, getdate, nowdate, today
from gym_management.gym_erp_system.notifications import send_freeze_email, send_auto_renew_email

DEFERRED_REVENUE_ACCOUNT = "Unearned Membership Revenue - GE"
AUTO_RENEW_PAYMENT_GRACE_DAYS = 5

def sync_member_status(member):
	"""Recompute Gym Member.membership_status from that member's Gym Subscriptions.
	Gym Subscription stays the source of truth; this keeps the Member list badge accurate."""
	if not member:
		return
	subs = frappe.get_all("Gym Subscription", filters={"member": member, "docstatus": 1}, fields=["status"])
	statuses = [s.status for s in subs]
	if "Frozen" in statuses:
		new_status = "Frozen"
	elif "Active" in statuses or "Scheduled" in statuses:
		new_status = "Active"
	elif statuses:
		new_status = "Expired"
	else:
		new_status = "Inactive"
	frappe.db.set_value("Gym Member", member, "membership_status", new_status)



def compute_end_date(start_date, duration_value, duration_unit, qty=1):
    total = (duration_value or 1) * (qty or 1)
    if duration_unit == "Days":
        return add_days(start_date, total - 1)
    elif duration_unit == "Weeks":
        return add_days(start_date, (total * 7) - 1)
    else:
        return add_days(add_months(start_date, total), -1)


def apply_deferred_revenue(doc, method=None):
    if not doc.get("gym_member"):
        return
    for item in doc.items:
        plan = frappe.db.get_value(
            "Gym Plan", {"item": item.item_code},
            ["name", "plan_group", "duration_value", "duration_unit", "one_time_charge"], as_dict=True
        )
        if not plan:
            continue
        if plan.one_time_charge:
            item.enable_deferred_revenue = 0
            continue
        duration_value = item.get("gym_package_duration_value") or plan.duration_value
        duration_unit = item.get("gym_package_duration_unit") or plan.duration_unit
        qty = int(item.qty or 1)
        total_months = (duration_value or 1) * qty if duration_unit == "Months" else 0
        if total_months > 1:
            start_date = get_start_date(doc.gym_member, plan.plan_group, doc.posting_date or today())
            end_date = compute_end_date(start_date, duration_value, duration_unit, qty)
            item.enable_deferred_revenue = 1
            item.service_start_date = start_date
            item.service_end_date = end_date
            item.deferred_revenue_account = DEFERRED_REVENUE_ACCOUNT
        else:
            item.enable_deferred_revenue = 0


def create_subscription_from_invoice(doc, method=None):
    if not doc.get("gym_member"):
        return
    for item in doc.items:
        if frappe.db.exists("Gym Subscription", {"sales_invoice_item": item.name, "docstatus": ["<", 2]}):
            continue
        plan = frappe.db.get_value(
            "Gym Plan", {"item": item.item_code},
            ["name", "plan_group", "duration_value", "duration_unit", "sessions", "one_time_charge"], as_dict=True
        )
        if not plan:
            continue
        if plan.one_time_charge:
            continue
        duration_value = item.get("gym_package_duration_value") or plan.duration_value
        duration_unit = item.get("gym_package_duration_unit") or plan.duration_unit
        qty = int(item.qty or 1)
        start_date = get_start_date(doc.gym_member, plan.plan_group, doc.posting_date or today())
        end_date = compute_end_date(start_date, duration_value, duration_unit, qty)
        current_date = getdate(nowdate())
        status = "Scheduled" if getdate(start_date) > current_date else "Active"
        total_sessions = (plan.sessions or 0) * qty
        sub = frappe.get_doc({
            "doctype": "Gym Subscription",
            "member": doc.gym_member,
            "gym_plan": plan.name,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "total_sessions": total_sessions,
            "sessions_used": 0,
            "sales_invoice": doc.name,
            "sales_invoice_item": item.name,
        })
        sub.flags.ignore_permissions = True
        sub.insert()
        sub.submit()
        sync_member_status(doc.gym_member)


def cancel_from_invoice(doc, method=None):
    subscriptions = frappe.get_all(
        "Gym Subscription", filters={"sales_invoice": doc.name, "docstatus": 1}, pluck="name"
    )
    for name in subscriptions:
        sub = frappe.get_doc("Gym Subscription", name)
        sub.flags.ignore_permissions = True
        sub.cancel()


def get_start_date(member, plan_group, posting_date):
    last_end = frappe.db.sql("""
        select max(s.end_date) from `tabGym Subscription` s
        join `tabGym Plan` p on p.name = s.gym_plan
        where s.member=%s and p.plan_group=%s and s.docstatus=1
          and s.status in ('Active', 'Scheduled', 'Frozen')
    """, (member, plan_group))
    if last_end and last_end[0][0]:
        last_end_date = getdate(last_end[0][0])
        post_date = getdate(posting_date)
        if last_end_date >= post_date:
            return add_days(last_end_date, 1)
    return getdate(posting_date)


def try_auto_renew(subscription_name):
    sub = frappe.db.get_value(
        "Gym Subscription", subscription_name,
        ["member", "gym_plan"], as_dict=True,
    )
    if not sub:
        return False
    plan = frappe.db.get_value(
        "Gym Plan", sub.gym_plan,
        ["item", "plan_name", "monthly_fee", "one_time_charge", "disabled"], as_dict=True,
    )
    if not plan or plan.one_time_charge or plan.disabled:
        return False
    member = frappe.db.get_value("Gym Member", sub.member, ["name", "customer"], as_dict=True)
    if not member or not member.customer:
        frappe.log_error(
            title="Gym Auto-Renew Failed",
            message="Gym Subscription {0}: member {1} has no linked Customer.".format(subscription_name, sub.member),
        )
        return False
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = member.customer
    inv.gym_member = member.name
    inv.due_date = add_days(nowdate(), AUTO_RENEW_PAYMENT_GRACE_DAYS)
    inv.append("items", {
        "item_code": plan.item,
        "qty": 1,
        "rate": plan.monthly_fee,
        "price_list_rate": plan.monthly_fee,
    })
    inv.insert(ignore_permissions=True)
    inv.submit()
    frappe.db.set_value("Gym Subscription", {"sales_invoice": inv.name}, "auto_renew", 1)
    new_end_date = frappe.db.get_value("Gym Subscription", {"sales_invoice": inv.name}, "end_date")
    frappe.db.commit()
    send_auto_renew_email(member.name, plan.plan_name, inv.name, new_end_date)
    return True


def update_expired_subscriptions():
    current_date = nowdate()
    expired_subs = frappe.get_all(
        "Gym Subscription",
        filters={"status": "Active", "end_date": ["<", current_date], "docstatus": 1},
        fields=["name", "auto_renew"],
    )
    for sub in expired_subs:
        frappe.db.set_value("Gym Subscription", sub.name, "status", "Expired")
        if sub.auto_renew:
            try:
                try_auto_renew(sub.name)
            except Exception:
                frappe.log_error(title="Gym Auto-Renew Failed", message=frappe.get_traceback())
    scheduled_subs = frappe.get_all(
        "Gym Subscription",
        filters={"status": "Scheduled", "start_date": ["<=", current_date], "docstatus": 1},
        pluck="name",
    )
    for name in scheduled_subs:
        frappe.db.set_value("Gym Subscription", name, "status", "Active")
    frozen_subs = frappe.get_all(
        "Gym Subscription",
        filters={"status": "Frozen", "freeze_end_date": ["<=", current_date], "docstatus": 1},
        pluck="name",
    )
    for name in frozen_subs:
        frappe.db.set_value("Gym Subscription", name, "status", "Active")

    affected_members = frappe.get_all(
        "Gym Subscription",
        filters={"name": ["in", [s.name for s in expired_subs] + scheduled_subs + frozen_subs]},
        pluck="member",
    ) if (expired_subs or scheduled_subs or frozen_subs) else []
    for member in set(affected_members):
        sync_member_status(member)

    frappe.db.commit()


@frappe.whitelist()
def freeze_subscription(subscription, freeze_days):
    freeze_days = int(freeze_days)
    if freeze_days <= 0:
        frappe.throw("Freeze days must be greater than zero.")
    sub = frappe.get_doc("Gym Subscription", subscription)
    if sub.status != "Active":
        frappe.throw("Only an Active subscription can be frozen.")
    new_end_date = add_days(sub.end_date, freeze_days)
    frappe.db.set_value("Gym Subscription", subscription, {
        "status": "Frozen",
        "freeze_start_date": nowdate(),
        "freeze_end_date": add_days(nowdate(), freeze_days),
        "end_date": new_end_date,
    })
    frappe.db.commit()
    sync_member_status(sub.member)
    send_freeze_email(subscription)
    return subscription


@frappe.whitelist()
def resume_subscription(subscription):
    sub = frappe.get_doc("Gym Subscription", subscription)
    if sub.status != "Frozen":
        frappe.throw("Only a Frozen subscription can be resumed.")
    current_date = getdate(nowdate())
    planned_freeze_end = getdate(sub.freeze_end_date)
    if current_date < planned_freeze_end:
        unused_days = (planned_freeze_end - current_date).days
        new_end_date = add_days(sub.end_date, -unused_days)
    else:
        new_end_date = sub.end_date
    frappe.db.set_value("Gym Subscription", subscription, {
        "status": "Active",
        "freeze_end_date": nowdate(),
        "end_date": new_end_date,
    })
    frappe.db.commit()
    sync_member_status(sub.member)
    return subscription


@frappe.whitelist()
def cancel_subscription(subscription, reason=None):
    sub = frappe.get_doc("Gym Subscription", subscription)
    if sub.status in ("Cancelled", "Expired"):
        frappe.throw("This subscription is already {0}.".format(sub.status))
    frappe.db.set_value("Gym Subscription", subscription, {
        "status": "Cancelled",
        "cancelled_on": nowdate(),
        "cancel_reason": reason or "",
    })
    frappe.db.commit()
    sync_member_status(sub.member)
    return subscription


def run_daily_backup():
    """Daily job: take a full site backup (database + files) so business data is never at risk of total loss."""
    try:
        from frappe.utils.backups import new_backup
        new_backup(ignore_files=False)
    except Exception:
        frappe.log_error(title="Gym Daily Backup Failed", message=frappe.get_traceback())
