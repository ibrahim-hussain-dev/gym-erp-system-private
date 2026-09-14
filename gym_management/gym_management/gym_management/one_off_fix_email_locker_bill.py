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


def run():
    # 1. notifications.py: add amount + due date line to the renewal email
    patch("apps/gym_management/gym_management/gym_erp_system/notifications.py", [
        (
'''def send_auto_renew_email(member, plan_name, new_invoice, new_end_date):
    email = get_member_email(member)
    full_name = _safe_full_name(member)
    subject = "Your Membership Has Been Auto-Renewed"
    message = \"\"\"
        <p>Dear {full_name},</p>
        <p>Your membership ({plan}) has been automatically renewed.</p>
        <p>New Invoice: <b>{invoice}</b><br>Your membership is now valid until <b>{end_date}</b>.</p>
        <p>If you did not want this, please contact the front desk to disable Auto-Renew.</p>
    \"\"\".format(full_name=full_name, plan=plan_name, invoice=new_invoice, end_date=new_end_date)
    safe_send(email, subject, message)''',
'''def send_auto_renew_email(member, plan_name, new_invoice, new_end_date, amount=None, due_date=None):
    email = get_member_email(member)
    full_name = _safe_full_name(member)
    subject = "Your Membership Has Been Auto-Renewed"
    payment_line = ""
    if amount is not None and due_date is not None:
        payment_line = "<p>Amount Due: <b>Rs {amount}</b><br>Please pay by <b>{due_date}</b> to avoid interruption.</p>".format(amount=amount, due_date=due_date)
    message = \"\"\"
        <p>Dear {full_name},</p>
        <p>Your membership ({plan}) has been automatically renewed.</p>
        <p>New Invoice: <b>{invoice}</b><br>Your membership is now valid until <b>{end_date}</b>.</p>
        {payment_line}
        <p>If you did not want this, please contact the front desk to disable Auto-Renew.</p>
    \"\"\".format(full_name=full_name, plan=plan_name, invoice=new_invoice, end_date=new_end_date, payment_line=payment_line)
    safe_send(email, subject, message)'''
        ),
    ])

    # 2. gym_subscription.py: pass amount + due date into the call
    patch("apps/gym_management/gym_management/gym_erp_system/gym_subscription.py", [
        (
'''    frappe.db.set_value("Gym Subscription", {"sales_invoice": inv.name}, "auto_renew", 1)
    new_end_date = frappe.db.get_value("Gym Subscription", {"sales_invoice": inv.name}, "end_date")
    frappe.db.commit()
    send_auto_renew_email(member.name, plan.plan_name, inv.name, new_end_date)
    return True''',
'''    frappe.db.set_value("Gym Subscription", {"sales_invoice": inv.name}, "auto_renew", 1)
    new_end_date = frappe.db.get_value("Gym Subscription", {"sales_invoice": inv.name}, "end_date")
    frappe.db.commit()
    send_auto_renew_email(member.name, plan.plan_name, inv.name, new_end_date, inv.grand_total, inv.due_date)
    return True'''
        ),
    ])

    # 3. sell_membership.js: don't auto-navigate away right after showing the bill dialog
    patch("apps/gym_management/gym_management/gym_erp_system/page/sell_membership/sell_membership.js", [
        (
'''                    bill_dialog.show();
                    let bill_frame = bill_dialog.$wrapper.find('#customer-bill-frame')[0];
                    if (bill_frame) {
                        bill_frame.onload = function() {
                            try {
                                let idoc = bill_frame.contentDocument || bill_frame.contentWindow.document;
                                let banner = idoc.querySelector('.action-banner');
                                if (banner) banner.style.display = 'none';
                            } catch (e) {}
                        };
                        bill_frame.src = preview_url;
                    }
                    frappe.set_route('Form', 'Sales Invoice', r.message.invoice);''',
'''                    bill_dialog.$wrapper.on('hidden.bs.modal', () => {
                        frappe.set_route('Form', 'Sales Invoice', r.message.invoice);
                    });
                    bill_dialog.show();
                    let bill_frame = bill_dialog.$wrapper.find('#customer-bill-frame')[0];
                    if (bill_frame) {
                        bill_frame.onload = function() {
                            try {
                                let idoc = bill_frame.contentDocument || bill_frame.contentWindow.document;
                                let banner = idoc.querySelector('.action-banner');
                                if (banner) banner.style.display = 'none';
                            } catch (e) {}
                        };
                        bill_frame.src = preview_url;
                    }'''
        ),
    ])

    # 4. Gym Plan: remove 'Locker' from plan_group options
    original_dev_mode = frappe.conf.developer_mode
    frappe.conf.developer_mode = 1
    try:
        dt = frappe.get_doc("DocType", "Gym Plan")
        changed = False
        for f in dt.fields:
            if f.fieldname == "plan_group" and f.options:
                opts = [o for o in f.options.split("\n") if o.strip() and o.strip() != "Locker"]
                new_options = "\n".join(opts)
                if new_options != f.options:
                    f.options = new_options
                    changed = True
        if changed:
            dt.save(ignore_permissions=True)
            frappe.db.commit()
            print("Removed 'Locker' from Gym Plan.plan_group options.")
        else:
            print("Gym Plan.plan_group already had no 'Locker' option, skipping.")
    finally:
        frappe.conf.developer_mode = original_dev_mode

    frappe.clear_cache()
    print("DONE")
