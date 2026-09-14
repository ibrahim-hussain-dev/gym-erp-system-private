import io
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


def ensure_custom_field(dt, fieldname, **kwargs):
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
        print(f"{dt}.{fieldname} already exists, skipping.")
        return
    doc = {"doctype": "Custom Field", "dt": dt, "fieldname": fieldname}
    doc.update(kwargs)
    frappe.get_doc(doc).insert(ignore_permissions=True)
    print(f"Created {dt}.{fieldname}")


def run():
    # 1. Sales Invoice.gym_member (needed for reports + receipt log)
    ensure_custom_field("Sales Invoice", "gym_member",
        label="Gym Member", fieldtype="Link", options="Gym Member",
        insert_after="customer", in_standard_filter=1)

    # 2. Sales Invoice Item package duration fields
    ensure_custom_field("Sales Invoice Item", "gym_package_duration_value",
        label="Gym Package Duration Value", fieldtype="Int", insert_after="item_code")
    ensure_custom_field("Sales Invoice Item", "gym_package_duration_unit",
        label="Gym Package Duration Unit", fieldtype="Select",
        options="Days\nWeeks\nMonths", insert_after="gym_package_duration_value")

    # NOTE: promo code fields (Gym Promo Code.times_used, Sales Invoice.promo_code)
    # deliberately NOT created here - promo code is being disabled on VPS, local-only for now.

    frappe.clear_cache()
    frappe.db.commit()

    # 3. Backfill gym_member on existing Sales Invoices from Gym Subscription
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

    # 4. Backfill member on existing Gym Customer Receipt logs
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

    # 5. Clean up dead fixture entries in hooks.py
    patch("apps/gym_management/gym_management/hooks.py", [
        (
'''    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Member"], ["fieldname", "=", "branch"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Trainer"], ["fieldname", "in", ["sessions_attended", "total_commission"]]]},
    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Trainer"]]},
    {"doctype": "Custom Field", "filters": [["dt", "=", "Gym Package Item"], ["fieldname", "=", "plan_price"]]},''',
'''    {"doctype": "Client Script", "filters": [["dt", "=", "Gym Trainer"]]},'''
        ),
    ])

    # 6. Hide Promo Code field in Sell Membership UI (VPS/client-facing) - keep code path intact, just not visible
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

    print("DONE")
