import io
import os
import shutil
import json
import frappe

BENCH = "/home/frappe/frappe-bench/"


def patch(path, replacements):
    full_path = BENCH + path
    with io.open(full_path, encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        if content.count(old) != 1:
            print(f"WARNING: anchor not found or not unique in {full_path}: {old[:80]!r}")
            continue
        content = content.replace(old, new, 1)
    with io.open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {full_path}")


def overwrite(path, content):
    full_path = BENCH + path
    with io.open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Overwrote {full_path}")


def ensure_custom_field(dt, fieldname, **kwargs):
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
        print(f"{dt}.{fieldname} already exists, skipping.")
        return
    doc = {"doctype": "Custom Field", "dt": dt, "fieldname": fieldname}
    doc.update(kwargs)
    frappe.get_doc(doc).insert(ignore_permissions=True)
    print(f"Created {dt}.{fieldname}")


def ensure_doctype_field(doctype, fieldname, insert_after, field_kwargs):
    original_dev_mode = frappe.conf.developer_mode
    frappe.conf.developer_mode = 1
    try:
        dt = frappe.get_doc("DocType", doctype)
        if any(f.fieldname == fieldname for f in dt.fields):
            print(f"{doctype}.{fieldname} (native field) already exists, skipping.")
            return
        idx = next((i for i, f in enumerate(dt.fields) if f.fieldname == insert_after), len(dt.fields) - 1)
        new_field = dt.append("fields", {})
        new_field.fieldname = fieldname
        for k, v in field_kwargs.items():
            setattr(new_field, k, v)
        dt.fields.remove(new_field)
        dt.fields.insert(idx + 1, new_field)
        for i, f in enumerate(dt.fields):
            f.idx = i + 1
        dt.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Added native field {doctype}.{fieldname}")
    finally:
        frappe.conf.developer_mode = original_dev_mode


def remove_workspace_shortcuts(workspace_name, labels_to_remove):
    ws = frappe.get_doc("Workspace", workspace_name)
    content = json.loads(ws.content) if isinstance(ws.content, str) else ws.content
    new_content = []
    removed_blocks = 0
    for block in content:
        data = block.get("data", {}) or {}
        if block.get("type") == "shortcut" and data.get("shortcut_name") in labels_to_remove:
            removed_blocks += 1
            continue
        new_content.append(block)
    ws.content = json.dumps(new_content)
    before = len(ws.shortcuts)
    ws.shortcuts = [s for s in ws.shortcuts if s.label not in labels_to_remove]
    after = len(ws.shortcuts)
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"Workspace '{workspace_name}': removed {removed_blocks} content block(s), shortcuts {before} -> {after}")


def run():
    gym_module = frappe.db.get_value("DocType", "Gym Member", "module")

    # ============ PART 1: pending invoices/reports fix ============
    ensure_custom_field("Sales Invoice", "gym_member",
        label="Gym Member", fieldtype="Link", options="Gym Member",
        insert_after="customer", in_standard_filter=1)
    ensure_custom_field("Sales Invoice Item", "gym_package_duration_value",
        label="Gym Package Duration Value", fieldtype="Int", insert_after="item_code")
    ensure_custom_field("Sales Invoice Item", "gym_package_duration_unit",
        label="Gym Package Duration Unit", fieldtype="Select",
        options="Days\nWeeks\nMonths", insert_after="gym_package_duration_value")
    frappe.clear_cache()
    frappe.db.commit()

    subs = frappe.get_all("Gym Subscription", filters={"sales_invoice": ["is", "set"]}, fields=["sales_invoice", "member"])
    inv_to_member = {}
    for s in subs:
        inv_to_member.setdefault(s.sales_invoice, s.member)
    backfilled = 0
    for inv_name, member in inv_to_member.items():
        current = frappe.db.get_value("Sales Invoice", inv_name, "gym_member")
        if not current and member:
            frappe.db.set_value("Sales Invoice", inv_name, "gym_member", member, update_modified=False)
            backfilled += 1
    print(f"Backfilled gym_member on {backfilled} existing Sales Invoice(s)")

    receipts = frappe.get_all("Gym Customer Receipt", fields=["name", "sales_invoice", "member"])
    r_backfilled = 0
    for r in receipts:
        if not r.member:
            inv_member = frappe.db.get_value("Sales Invoice", r.sales_invoice, "gym_member")
            if inv_member:
                frappe.db.set_value("Gym Customer Receipt", r.name, "member", inv_member, update_modified=False)
                r_backfilled += 1
    print(f"Backfilled member on {r_backfilled} existing Gym Customer Receipt log(s)")
    frappe.db.commit()

    patch("apps/gym_management/gym_management/hooks.py", [
        (
'''    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Member"], ["fieldname", "=", "branch"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Trainer"], ["fieldname", "in", ["sessions_attended", "total_commission"]]]},
    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Trainer"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Package Item"], ["fieldname", "=", "plan_price"]]},''',
'''    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Trainer"]]},'''
        ),
    ])

    patch("apps/gym_management/gym_management/gym_erp_system/page/sell_membership/sell_membership.js", [
        (
'''                {
                    fieldname: 'promo_code',
                    fieldtype: 'Data',
                    label: 'Promo Code (optional)',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },''',
'''                {
                    fieldname: 'promo_code',
                    fieldtype: 'Data',
                    label: 'Promo Code (optional)',
                    hidden: 1,
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },'''
        ),
    ])

    # ============ PART 2: remove PT slot booking feature entirely ============
    patch("apps/gym_management/gym_management/gym_erp_system/api.py", [
        (
'''    exp.insert(ignore_permissions=True)
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
def mark_attendance(member):''',
'''    exp.insert(ignore_permissions=True)
    exp.submit()
    return {"name": exp.name, "journal_entry": exp.journal_entry}


@frappe.whitelist()
def mark_attendance(member):'''
        ),
        (
'''@frappe.whitelist()
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
    return {"sessions_attended": sessions, "total_commission": sessions * price}''',
'''@frappe.whitelist()
def get_trainer_commission_stats(trainer):
    total = frappe.db.get_value("Gym Trainer", trainer, "total_commission_earned") or 0
    sales_logged = frappe.db.count("Gym Trainer Commission", {"trainer": trainer})
    return {"sales_logged": sales_logged, "total_commission": flt(total)}'''
        ),
    ])

    patch("apps/gym_management/gym_management/gym_erp_system/notifications.py", [
        (
'''def send_noshow_email(slot_name):
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
    safe_send(email, subject, message)''',
''''''
        ),
    ])

    patch("apps/gym_management/gym_management/hooks.py", [
        (
'''        "on_submit": "gym_management.gym_erp_system.gym_subscription.create_subscription_from_invoice",''',
'''        "on_submit": [
            "gym_management.gym_erp_system.gym_subscription.create_subscription_from_invoice",
            "gym_management.gym_erp_system.trainer_commission.log_commission_from_invoice"
        ],'''
        ),
        (
'''        "gym_management.gym_erp_system.gym_subscription.update_expired_subscriptions",
        "gym_management.gym_erp_system.gym_slot.mark_noshow_slots",
        "gym_management.gym_erp_system.notifications.send_expiry_reminders",''',
'''        "gym_management.gym_erp_system.gym_subscription.update_expired_subscriptions",
        "gym_management.gym_erp_system.notifications.send_expiry_reminders",'''
        ),
    ])

    remove_workspace_shortcuts("Impact Health Studio", ["Book Pt Session", "Book PT Session", "Gym Slot"])

    slot_count = frappe.db.count("Gym Slot")
    if slot_count == 0:
        for page_name in ["book-pt-session", "Book PT Session", "book_pt_session"]:
            if frappe.db.exists("Page", page_name):
                frappe.delete_doc("Page", page_name, ignore_permissions=True, force=True)
                print(f"Deleted Page: {page_name}")
                break
        else:
            print("WARNING: could not find 'Book PT Session' Page record to delete - check manually.")

        if frappe.db.exists("DocType", "Gym Slot"):
            frappe.delete_doc("DocType", "Gym Slot", ignore_permissions=True, force=True)
            print("Deleted DocType: Gym Slot")

        frappe.db.commit()

        page_folder = BENCH + "apps/gym_management/gym_management/gym_erp_system/page/book_pt_session"
        if os.path.exists(page_folder):
            shutil.rmtree(page_folder)
            print("Removed folder:", page_folder)

        doctype_folder = BENCH + "apps/gym_management/gym_management/gym_erp_system/doctype/gym_slot"
        if os.path.exists(doctype_folder):
            shutil.rmtree(doctype_folder)
            print("Removed folder:", doctype_folder)

        slot_module = BENCH + "apps/gym_management/gym_management/gym_erp_system/gym_slot.py"
        if os.path.exists(slot_module):
            os.remove(slot_module)
            print("Removed file:", slot_module)
    else:
        print(f"Gym Slot has {slot_count} existing record(s) - NOT deleting doctype/data. Skipped destructive cleanup; only code/UI removal applied.")

    # ============ PART 3: new plan-price-percentage commission system ============
    ensure_doctype_field("Gym Plan", "trainer", "plan_group", {
        "fieldtype": "Link", "options": "Gym Trainer", "label": "Trainer",
        "depends_on": 'eval:doc.plan_group=="Personal Training"',
    })
    ensure_doctype_field("Gym Trainer", "commission_percentage", "price_per_session", {
        "fieldtype": "Percent", "label": "Commission Percentage",
        "description": "Trainer's fixed cut of each PT plan sale, e.g. 40 for 40%.",
    })
    ensure_doctype_field("Gym Trainer", "total_commission_earned", "commission_percentage", {
        "fieldtype": "Currency", "label": "Total Commission Earned", "read_only": 1, "default": "0",
    })

    if not frappe.db.exists("DocType", "Gym Trainer Commission"):
        original_dev_mode = frappe.conf.developer_mode
        frappe.conf.developer_mode = 1
        try:
            dt = frappe.get_doc({
                "doctype": "DocType",
                "name": "Gym Trainer Commission",
                "module": gym_module,
                "custom": 0,
                "istable": 0,
                "editable_grid": 1,
                "track_changes": 1,
                "autoname": "hash",
                "fields": [
                    {"fieldname": "trainer", "fieldtype": "Link", "label": "Trainer", "options": "Gym Trainer", "reqd": 1, "in_list_view": 1},
                    {"fieldname": "sales_invoice", "fieldtype": "Link", "label": "Sales Invoice", "options": "Sales Invoice", "reqd": 1, "in_list_view": 1},
                    {"fieldname": "member", "fieldtype": "Link", "label": "Gym Member", "options": "Gym Member"},
                    {"fieldname": "gym_plan", "fieldtype": "Link", "label": "Gym Plan", "options": "Gym Plan", "in_list_view": 1},
                    {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                    {"fieldname": "sale_amount", "fieldtype": "Currency", "label": "Sale Amount"},
                    {"fieldname": "commission_percentage", "fieldtype": "Percent", "label": "Commission %"},
                    {"fieldname": "commission_amount", "fieldtype": "Currency", "label": "Commission Amount", "in_list_view": 1},
                    {"fieldname": "date", "fieldtype": "Date", "label": "Date", "in_list_view": 1},
                ],
                "permissions": [
                    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
                    {"role": "Gym Owner", "read": 1, "report": 1, "export": 1, "print": 1},
                ],
            })
            dt.insert(ignore_permissions=True)
            frappe.db.commit()
            print("Created DocType: Gym Trainer Commission (Gym Owner + System Manager access only)")
        finally:
            frappe.conf.developer_mode = original_dev_mode
    else:
        print("Gym Trainer Commission DocType already exists, skipping.")

    frappe.clear_cache()
    print("DONE")
