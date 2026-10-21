import json
import frappe
from frappe.utils import add_days, flt, getdate, nowdate, nowtime, today


def _require_roles(*allowed_roles):
    """Defense-in-depth: block direct API calls from users whose role isn't allowed,
    even though the corresponding page is already hidden from them in the UI."""
    always_allowed = {"Administrator", "System Manager"}
    user_roles = set(frappe.get_roles())
    if not user_roles & (set(allowed_roles) | always_allowed):
        frappe.throw("You are not permitted to perform this action.", frappe.PermissionError)


@frappe.whitelist()
def get_billing_preview(plans=None, member=None, quantities=None, discounts=None, package=None, overall_discount_type=None, overall_discount_value=0, override_start_date=None):
    if isinstance(plans, str):
        plans = json.loads(plans)
    plans = plans or []
    if isinstance(discounts, str):
        discounts = json.loads(discounts) if discounts else {}
    discounts = discounts or {}
    if isinstance(quantities, str):
        quantities = json.loads(quantities) if quantities else {}
    quantities = quantities or {}
    from gym_management.gym_erp_system.gym_subscription import get_start_date, compute_end_date
    from gym_management.gym_erp_system.gym_package import resolve_package_rows
    rows = []
    for plan_name in plans:
        plan = frappe.db.get_value(
            "Gym Plan", plan_name,
            ["plan_name", "plan_group", "duration_value", "duration_unit", "monthly_fee", "one_time_charge"], as_dict=True
        )
        if not plan:
            continue
        rows.append({
            "key": plan_name,
            "plan_name": plan.plan_name,
            "plan_group": plan.plan_group,
            "unit_price": flt(plan.monthly_fee),
            "duration_value": plan.duration_value,
            "duration_unit": plan.duration_unit,
            "one_time_charge": plan.one_time_charge,
        })
    if package:
        for r in resolve_package_rows(package):
            rows.append({
                "key": package + "::" + r["gym_plan"],
                "plan_name": r["plan_name"] + " (via " + package + ")",
                "plan_group": r["plan_group"],
                "unit_price": r["unit_price"],
                "duration_value": r["duration_value"],
                "duration_unit": r["duration_unit"],
                "one_time_charge": r["one_time_charge"],
            })
    lines = []
    total = 0
    local_group_end = {}
    for row in rows:
        if row["one_time_charge"]:
            gross_amount = row["unit_price"]
            net_amount, discount_amount = apply_line_discount(gross_amount, discounts.get(row["key"]))
            total += net_amount
            lines.append({
                "plan": row["plan_name"], "key": row["key"], "one_time": 1,
                "start_date": None, "end_date": None,
                "gross_amount": gross_amount, "discount_amount": discount_amount, "amount": net_amount,
            })
            continue
        if override_start_date:
            base_start = getdate(override_start_date)
        else:
            base_start = get_start_date(member, row["plan_group"], today()) if member else getdate(today())
        if row["plan_group"] in local_group_end and local_group_end[row["plan_group"]] >= base_start:
            start_date = add_days(getdate(local_group_end[row["plan_group"]]), 1)
        else:
            start_date = base_start
        qty = int(quantities.get(row["key"]) or 1)
        end_date = compute_end_date(start_date, row["duration_value"], row["duration_unit"], qty)
        local_group_end[row["plan_group"]] = getdate(end_date)
        gross_amount = row["unit_price"] * qty
        net_amount, discount_amount = apply_line_discount(gross_amount, discounts.get(row["key"]))
        total += net_amount
        lines.append({
            "plan": row["plan_name"], "key": row["key"], "one_time": 0,
            "start_date": start_date, "end_date": end_date,
            "gross_amount": gross_amount, "discount_amount": discount_amount, "amount": net_amount,
        })
    if overall_discount_type and overall_discount_type != "None" and flt(overall_discount_value) > 0:
        if overall_discount_type == "Percentage":
            if flt(overall_discount_value) > 100:
                frappe.throw("Overall discount percentage cannot exceed 100%.")
            total = total - (total * flt(overall_discount_value) / 100)
        elif overall_discount_type == "Fixed Amount":
            if flt(overall_discount_value) > total:
                frappe.throw("Overall discount (Rs {0}) cannot exceed the total amount (Rs {1}).".format(overall_discount_value, total))
            total = total - flt(overall_discount_value)
    return {"total_amount": total, "lines": lines}


def apply_line_discount(gross_amount, discount):
    if not discount:
        return gross_amount, 0
    discount_type = discount.get("type")
    value = flt(discount.get("value"))
    if not discount_type or discount_type == "None" or value <= 0:
        return gross_amount, 0
    if discount_type == "Percentage":
        if value > 100:
            frappe.throw("Discount percentage cannot exceed 100%.")
        discount_amount = gross_amount * value / 100
    elif discount_type == "Fixed Amount":
        discount_amount = value
    else:
        return gross_amount, 0
    if discount_amount > gross_amount:
        frappe.throw(
            "Discount (Rs {0}) cannot exceed the item amount (Rs {1}).".format(discount_amount, gross_amount)
        )
    return gross_amount - discount_amount, discount_amount


@frappe.whitelist()
def sell_membership(
    plans=None, member=None, is_new_member=0, full_name=None, phone=None, email=None,
    national_id_cnic=None, member_photo=None, gender=None, height_feet=None, weight_kg=None,
    fitness_goal=None, preferred_workout_time=None, alternative_workout_time=None, medical_conditions=None, health_issue=None,
    activity_level=None, workout_history=None,
    emergency_contact_name=None, emergency_contact_phone=None,
    quantities=None, discounts=None, amount_received=0,
    mode_of_payment="Cash", payment_due_date=None, package=None, auto_renew=0,
    overall_discount_type=None, overall_discount_value=0, start_date=None,
):
    _require_roles("Gym Front Desk", "Gym Owner")
    if isinstance(plans, str):
        plans = json.loads(plans)
    plans = plans or []
    if isinstance(discounts, str):
        discounts = json.loads(discounts) if discounts else {}
    discounts = discounts or {}
    if isinstance(quantities, str):
        quantities = json.loads(quantities) if quantities else {}
    quantities = quantities or {}
    if not plans and not package:
        frappe.throw("Select at least one plan or a package.")
    if int(is_new_member or 0):
        if not full_name or not phone or not email:
            frappe.throw("Full Name, Phone, and Email are required to register a new member.")
        member_doc = frappe.new_doc("Gym Member")
        member_doc.full_name = full_name
        member_doc.phone = phone
        member_doc.email = email
        member_doc.national_id_cnic = national_id_cnic
        member_doc.member_photo = member_photo
        member_doc.gender = gender
        member_doc.height_feet = height_feet
        member_doc.weight_kg = weight_kg
        member_doc.fitness_goal = fitness_goal
        member_doc.preferred_workout_time = preferred_workout_time
        member_doc.alternative_workout_time = alternative_workout_time
        member_doc.medical_conditions = medical_conditions
        member_doc.health_issue = health_issue
        member_doc.activity_level = activity_level
        member_doc.workout_history = workout_history
        member_doc.emergency_contact_name = emergency_contact_name
        member_doc.emergency_contact_phone = emergency_contact_phone
        member_doc.joining_date = nowdate()
        member_doc.insert(ignore_permissions=True)
        member = member_doc.name
        if flt(weight_kg) or flt(height_feet):
            _height_cm_calc = flt(height_feet) * 30.48 if height_feet else None
            frappe.get_doc({
                "doctype": "Gym Fitness Log",
                "member": member,
                "log_date": nowdate(),
                "weight_kg": weight_kg,
                "height_cm": _height_cm_calc,
                "notes": "Baseline (recorded at registration)",
            }).insert(ignore_permissions=True)
    else:
        if not member:
            frappe.throw("Select an existing member or mark this as a New Member.")
    gym_member = frappe.get_doc("Gym Member", member)
    if not gym_member.customer:
        frappe.throw("This member is not linked to a Customer.")
    from gym_management.gym_erp_system.gym_package import resolve_package_rows
    inv = frappe.new_doc("Sales Invoice")
    inv.customer = gym_member.customer
    inv.gym_member = member
    rows = []
    for plan_name in plans:
        plan = frappe.get_doc("Gym Plan", plan_name)
        if plan.disabled:
            frappe.throw(f"Plan {plan.plan_name} is disabled.")
        rows.append({
            "key": plan_name,
            "item": plan.item,
            "plan_name": plan.plan_name,
            "one_time_charge": plan.one_time_charge,
            "unit_price": None,
            "monthly_fee": flt(plan.monthly_fee),
        })
    if package:
        for r in resolve_package_rows(package):
            rows.append({
                "key": package + "::" + r["gym_plan"],
                "item": r["item"],
                "plan_name": r["plan_name"],
                "one_time_charge": r["one_time_charge"],
                "unit_price": r["unit_price"],
                "monthly_fee": r["unit_price"],
                "package_duration_value": r["duration_value"],
                "package_duration_unit": r["duration_unit"],
            })
    for row in rows:
        item_qty = 1 if row["one_time_charge"] else int(quantities.get(row["key"]) or 1)
        line = {"item_code": row["item"], "qty": item_qty}
        if row["unit_price"] is not None:
            line["rate"] = row["unit_price"]
            line["price_list_rate"] = row["unit_price"]
        if row.get("package_duration_value"):
            line["gym_package_duration_value"] = row["package_duration_value"]
            line["gym_package_duration_unit"] = row["package_duration_unit"]
        discount = discounts.get(row["key"])
        if discount:
            discount_type = discount.get("type")
            value = flt(discount.get("value"))
            base_price = row["monthly_fee"]
            if discount_type == "Percentage" and value > 0:
                if value > 100:
                    frappe.throw("Discount percentage cannot exceed 100%.")
                line["discount_percentage"] = value
            elif discount_type == "Fixed Amount" and value > 0:
                gross_line_total = flt(base_price) * item_qty
                if value > gross_line_total:
                    frappe.throw(
                        "Discount (Rs {0}) on {1} cannot exceed its amount (Rs {2}).".format(
                            value, row["plan_name"], gross_line_total
                        )
                    )
                line["discount_amount"] = value / item_qty
        inv.append("items", line)
    if payment_due_date:
        inv.due_date = payment_due_date
    if overall_discount_type and overall_discount_type != "None" and flt(overall_discount_value) > 0:
        inv.apply_discount_on = "Grand Total"
        if overall_discount_type == "Percentage":
            if flt(overall_discount_value) > 100:
                frappe.throw("Overall discount percentage cannot exceed 100%.")
            inv.additional_discount_percentage = flt(inv.additional_discount_percentage or 0) + flt(overall_discount_value)
        elif overall_discount_type == "Fixed Amount":
            inv.discount_amount = flt(inv.discount_amount or 0) + flt(overall_discount_value)
    inv.insert(ignore_permissions=True)
    inv.submit()
    if int(auto_renew or 0):
        frappe.db.set_value("Gym Subscription", {"sales_invoice": inv.name}, "auto_renew", 1)
    if start_date:
        from gym_management.gym_erp_system.gym_subscription import override_subscription_start_dates
        override_subscription_start_dates(inv.name, getdate(start_date))
    payment_entry = None
    amount_received = flt(amount_received)
    if amount_received > 0:
        if amount_received > inv.grand_total:
            frappe.throw(
                "Amount received (Rs {0}) cannot exceed the invoice total (Rs {1}).".format(
                    amount_received, inv.grand_total
                )
            )
        payment_entry = create_payment_entry(inv, amount_received, mode_of_payment)
    inv.reload()
    return {
        "member": member, "invoice": inv.name, "grand_total": inv.grand_total,
        "outstanding_amount": inv.outstanding_amount, "due_date": inv.due_date,
        "payment_entry": payment_entry,
    }


def create_payment_entry(invoice, amount, mode_of_payment):
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Sales Invoice", invoice.name)
    pe.mode_of_payment = mode_of_payment
    pe.paid_amount = amount
    pe.received_amount = amount
    pe.reference_no = invoice.name
    pe.reference_date = nowdate()
    for row in pe.references:
        row.allocated_amount = amount
    if not pe.paid_to:
        pe.paid_to = get_default_cash_account()
    pe.insert(ignore_permissions=True)
    pe.submit()
    return pe.name


def get_default_cash_account():
    company = frappe.get_cached_doc("Company", "Gym ERP")
    account = company.default_cash_account or company.default_bank_account
    if not account:
        frappe.throw(
            "No Default Cash Account or Default Bank Account is set on Company 'Gym ERP'. "
            "Set one before recording payments at time of sale."
        )
    return account


@frappe.whitelist()
def record_expense(expense_date, category, amount, payment_method="Cash", paid_to=None, description=None, receipt=None):
    _require_roles("Gym Front Desk", "Gym Owner")
    amount = flt(amount)
    if amount <= 0:
        frappe.throw("Amount must be greater than zero.")
    exp = frappe.new_doc("Gym Expense")
    exp.expense_date = expense_date
    exp.category = category
    exp.amount = amount
    exp.payment_method = payment_method
    exp.paid_to = paid_to
    exp.description = description
    exp.receipt = receipt
    exp.insert(ignore_permissions=True)
    exp.submit()
    return {"name": exp.name, "journal_entry": exp.journal_entry}


WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _is_weekday_in_range(weekday, day_from, day_to):
    order = {d: i for i, d in enumerate(WEEKDAY_NAMES)}
    start, end, target = order[day_from], order[day_to], order[weekday]
    if start <= end:
        return start <= target <= end
    return target >= start or target <= end


@frappe.whitelist()
def get_trainer_windows(trainer, date):
    weekday = WEEKDAY_NAMES[getdate(date).weekday()]
    rows = frappe.get_all(
        "Gym Trainer Availability",
        filters={"parent": trainer},
        fields=["day_from", "day_to", "start_time", "end_time"],
    )
    return [
        {"start_time": r.start_time, "end_time": r.end_time}
        for r in rows if _is_weekday_in_range(weekday, r.day_from, r.day_to)
    ]


@frappe.whitelist()
def book_pt_slot(member, gym_subscription, trainer, date, start_time, end_time):
    sub = frappe.db.get_value(
        "Gym Subscription", gym_subscription,
        ["member", "status", "sessions_used", "total_sessions"], as_dict=True
    )
    if not sub or sub.member != member:
        frappe.throw("Selected subscription does not belong to this member.")
    if sub.status not in ("Active", "Scheduled"):
        frappe.throw("This subscription is not Active.")
    if (sub.sessions_used or 0) >= (sub.total_sessions or 0):
        frappe.throw("This member has no sessions remaining in this pack.")
    slot = frappe.get_doc({
        "doctype": "Gym Slot",
        "member": member,
        "gym_subscription": gym_subscription,
        "trainer": trainer,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "status": "Scheduled",
    })
    slot.insert(ignore_permissions=True)
    return slot.name


@frappe.whitelist()
def mark_attendance(member):
    if frappe.db.exists("Gym Attendance", {"member": member, "date": nowdate()}):
        frappe.throw("Attendance for this member is already marked for today.")
    att = frappe.get_doc({
        "doctype": "Gym Attendance",
        "member": member,
        "date": nowdate(),
        "check_in_time": nowtime(),
        "source": "Manual",
    })
    att.insert(ignore_permissions=True)
    return {"name": att.name}


@frappe.whitelist()
def get_trainer_commission_stats(trainer):
    row = frappe.db.sql("""
        select
            count(gs.name) as sessions_attended,
            gt.price_per_session
        from `tabGym Trainer` gt
        left join `tabGym Slot` gs on gs.trainer = gt.name and gs.status = 'Attended'
        where gt.name = %s
        group by gt.name
    """, (trainer,), as_dict=True)
    if not row:
        return {"sessions_attended": 0, "total_commission": 0}
    r = row[0]
    sessions = r.sessions_attended or 0
    price = flt(r.price_per_session)
    return {"sessions_attended": sessions, "total_commission": sessions * price}


@frappe.whitelist()
def get_member_subscriptions(member):
    subs = frappe.get_all(
        "Gym Subscription",
        filters={"member": member, "docstatus": 1, "status": ["in", ["Active", "Scheduled", "Frozen"]]},
        fields=["name", "gym_plan", "status", "start_date", "end_date", "freeze_end_date"],
        order_by="start_date desc",
    )
    plan_ids = list({s.gym_plan for s in subs if s.gym_plan})
    plan_names = {}
    if plan_ids:
        for p in frappe.get_all("Gym Plan", filters={"name": ["in", plan_ids]}, fields=["name", "plan_name"]):
            plan_names[p.name] = p.plan_name
    for s in subs:
        s["gym_plan_name"] = plan_names.get(s.gym_plan) or s.gym_plan
    return subs


@frappe.whitelist()
def get_member_summary(member):
    """Quick history shown when staff pick an existing member in the Sell/
    Renew dialog: has registration been paid, and what is their most recent
    plan (by end_date) and its status/expiry. Registration is detected via
    any submitted Sales Invoice Item against a one_time_charge Gym Plan --
    the only such plan in this gym's catalog today. Gym Subscription never
    contains one-time-charge plans (create_subscription_from_invoice skips
    them), so the "last plan" lookup naturally excludes registration."""
    if not member or not frappe.db.exists("Gym Member", member):
        return {}
    registration_paid = bool(frappe.db.sql("""
        select 1
        from `tabSales Invoice Item` sii
        join `tabSales Invoice` si on si.name = sii.parent
        join `tabGym Plan` gp on gp.item = sii.item_code
        where si.gym_member = %s and si.docstatus = 1 and gp.one_time_charge = 1
        limit 1
    """, (member,)))
    last_sub = frappe.get_all(
        "Gym Subscription",
        filters={"member": member, "docstatus": 1},
        fields=["gym_plan", "status", "end_date"],
        order_by="end_date desc",
        limit_page_length=1,
    )
    last_plan_name = None
    last_plan_status = None
    last_plan_end_date = None
    if last_sub:
        row = last_sub[0]
        last_plan_name = frappe.db.get_value("Gym Plan", row.gym_plan, "plan_name") if row.gym_plan else None
        last_plan_status = row.status
        last_plan_end_date = row.end_date
    return {
        "registration_paid": registration_paid,
        "last_plan_name": last_plan_name,
        "last_plan_status": last_plan_status,
        "last_plan_end_date": last_plan_end_date,
    }


def _can_delete_financial_records():
    """Only the Gym Owner (plus Administrator/System Manager, and the
    specific account iibrahihere@gmail.com) may permanently wipe a
    member's financial records. Gym Front Desk can still use the normal
    delete (subscription/attendance/fitness log, invoices preserved) --
    this check only gates the opt-in delete_financial_records=1 path."""
    if frappe.session.user == "iibrahihere@gmail.com":
        return True
    always_allowed_roles = {"Administrator", "System Manager"}
    user_roles = set(frappe.get_roles())
    return bool(user_roles & (always_allowed_roles | {"Gym Owner"}))


@frappe.whitelist()
def delete_gym_member(member, delete_financial_records=0):
    """Permanently delete a Gym Member along with their Gym Subscription,
    Gym Attendance, and Gym Fitness Log records.

    By default, Sales Invoice, Gym Customer Receipt, and Gym Trainer
    Commission records are left untouched -- these are financial/payout
    records kept for accounting purposes.

    Pass delete_financial_records=1 (an explicit, opt-in, type-to-confirm
    checkbox on the delete dialog -- restricted to the Gym Owner, see
    _can_delete_financial_records) to ALSO permanently delete those
    financial records, plus any Payment Entry linked to one of this
    member's Sales Invoices (deleted first, since Frappe will not let a
    Sales Invoice with a submitted Payment Entry reference against it be
    cancelled). Intended only for rare cases such as a member entered
    entirely by mistake, where there is no real financial history worth
    preserving. This cannot be undone.

    The member's linked Customer record is always left untouched, even on
    a full financial wipe, since other data outside this member's own
    records may still reference it. force=True on every delete bypasses
    the link-exists check so documents we're intentionally leaving alone
    don't block the delete; Frappe simply keeps the old member/invoice ID
    as a plain, non-resolving value on whatever (if anything) still
    references them afterward."""
    _require_roles("Gym Front Desk", "Gym Owner")
    if not frappe.db.exists("Gym Member", member):
        frappe.throw("Gym Member {0} does not exist.".format(member))

    delete_financial_records = int(delete_financial_records or 0)

    if delete_financial_records and not _can_delete_financial_records():
        frappe.throw(
            "Only the Gym Owner can permanently delete a member's financial records.",
            frappe.PermissionError,
        )

    deleted_counts = {"Gym Subscription": 0, "Gym Attendance": 0, "Gym Fitness Log": 0}

    for doctype in ("Gym Subscription", "Gym Attendance", "Gym Fitness Log"):
        names = frappe.get_all(doctype, filters={"member": member}, pluck="name")
        for name in names:
            _force_delete(doctype, name)
            deleted_counts[doctype] += 1

    if delete_financial_records:
        deleted_counts["Payment Entry"] = 0
        deleted_counts["Sales Invoice"] = 0
        deleted_counts["Gym Customer Receipt"] = 0
        deleted_counts["Gym Trainer Commission"] = 0

        invoice_names = frappe.get_all("Sales Invoice", filters={"gym_member": member}, pluck="name")
        for inv_name in invoice_names:
            payment_entry_names = frappe.get_all(
                "Payment Entry Reference",
                filters={"reference_doctype": "Sales Invoice", "reference_name": inv_name},
                pluck="parent",
            )
            for pe_name in set(payment_entry_names):
                if frappe.db.exists("Payment Entry", pe_name):
                    _force_delete("Payment Entry", pe_name)
                    deleted_counts["Payment Entry"] += 1
            _force_delete("Sales Invoice", inv_name)
            deleted_counts["Sales Invoice"] += 1

        receipt_names = frappe.get_all("Gym Customer Receipt", filters={"member": member}, pluck="name")
        for name in receipt_names:
            _force_delete("Gym Customer Receipt", name)
            deleted_counts["Gym Customer Receipt"] += 1

        commission_names = frappe.get_all("Gym Trainer Commission", filters={"member": member}, pluck="name")
        for name in commission_names:
            _force_delete("Gym Trainer Commission", name)
            deleted_counts["Gym Trainer Commission"] += 1

    _force_delete("Gym Member", member)
    frappe.db.commit()
    return {
        "deleted_member": member,
        "deleted_counts": deleted_counts,
        "financial_records_deleted": bool(delete_financial_records),
    }


def _force_delete(doctype, name):
    """Cancel first if the document is submitted (Frappe refuses to delete a
    submitted doc otherwise), then delete it, bypassing the link-exists
    check (force=True) so documents we're intentionally leaving alone
    elsewhere don't block the delete."""
    doc = frappe.get_doc(doctype, name)
    if doc.meta.is_submittable and doc.docstatus == 1:
        doc.flags.ignore_permissions = True
        doc.cancel()
    frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
