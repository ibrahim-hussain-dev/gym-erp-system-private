import io
import frappe

BENCH = "/home/frappe/frappe-bench/"

RECEIPT_TEMPLATE = """
<style>
  @page {
    size: 80mm auto;
    margin: 5mm 3mm;
  }
  .print-format {
    min-height: auto !important;
    max-width: 320px !important;
    padding: 10px !important;
  }
  * { box-sizing: border-box; }
  .receipt { font-family: 'Courier New', monospace; font-size: 11.5px; color: #000; width: 100%; max-width: 290px; margin: 0 auto; line-height: 1.55; }
  .receipt .center { text-align: center; }
  .receipt .bold { font-weight: bold; }
  .receipt .big { font-size: 15px; font-weight: bold; }
  .receipt .small { font-size: 10px; color: #333; }
  .receipt .dashed { border-top: 1px dashed #000; margin: 7px 0; }
  .receipt table { width: 100%; border-collapse: collapse; }
  .receipt td { padding: 1px 0; vertical-align: top; }
  .receipt .item-name { font-weight: bold; }
  .receipt .item-sub { font-size: 10px; color: #333; }
  .receipt .amt { text-align: right; white-space: nowrap; }
  .receipt .status-line { text-align: center; font-weight: bold; letter-spacing: 1px; margin: 7px 0; padding: 4px 0; border-top: 1px solid #000; border-bottom: 1px solid #000; }
  .receipt .foot { text-align: center; margin-top: 10px; font-size: 10px; color: #333; }
</style>

{% set paid_amount = doc.grand_total - doc.outstanding_amount %}
{% set pe_rows = frappe.get_all("Payment Entry Reference", filters={"reference_doctype": "Sales Invoice", "reference_name": doc.name}, fields=["parent"], order_by="creation desc", limit_page_length=1) %}
{% set last_pe = frappe.get_doc("Payment Entry", pe_rows[0].parent) if pe_rows else None %}
{% set member_info = frappe.db.get_value("Gym Member", doc.gym_member, ["full_name", "phone", "email"], as_dict=True) if doc.get("gym_member") else None %}
{% if doc.outstanding_amount <= 0 %}
  {% set status_label = "*** PAID ***" %}
{% elif paid_amount > 0 %}
  {% set status_label = "* PARTLY PAID *" %}
{% else %}
  {% set status_label = "*** UNPAID ***" %}
{% endif %}

<div class="receipt">
  <div class="center big">{{ doc.company }}</div>
  <div class="center small">Customer Bill / Payment Receipt</div>
  <div class="dashed"></div>

  <div>Bill No : {{ doc.name }}</div>
  <div>Date    : {{ frappe.utils.format_datetime(doc.creation, "dd-MM-yyyy hh:mm a") }}</div>
  {% if last_pe %}<div>Payment : {{ frappe.utils.format_datetime(last_pe.creation, "dd-MM-yyyy hh:mm a") }}</div>{% endif %}
  <div class="dashed"></div>

  <div class="bold">Bill To:</div>
  <div>{{ member_info.full_name if member_info else doc.customer_name }}</div>
  {% if member_info and member_info.phone %}<div>{{ member_info.phone }}</div>{% endif %}
  <div class="dashed"></div>

  <table>
    {% for item in doc.items %}
    <tr>
      <td colspan="2" class="item-name">{{ item.item_name }}</td>
    </tr>
    <tr>
      <td class="item-sub">{{ item.qty }} x {{ frappe.utils.fmt_money(item.price_list_rate or item.rate, currency=doc.currency) }}</td>
      <td class="amt">{{ frappe.utils.fmt_money(item.amount, currency=doc.currency) }}</td>
    </tr>
    {% endfor %}
  </table>
  <div class="dashed"></div>

  <table>
    <tr><td>Sub Total</td><td class="amt">{{ frappe.utils.fmt_money(doc.net_total, currency=doc.currency) }}</td></tr>
    {% if doc.discount_amount %}
    <tr><td>Discount</td><td class="amt">-{{ frappe.utils.fmt_money(doc.discount_amount, currency=doc.currency) }}</td></tr>
    {% endif %}
    <tr class="bold"><td>Grand Total</td><td class="amt">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
    <tr><td>Paid</td><td class="amt">{{ frappe.utils.fmt_money(paid_amount, currency=doc.currency) }}</td></tr>
    <tr class="bold"><td>Balance Due</td><td class="amt">{{ frappe.utils.fmt_money(doc.outstanding_amount, currency=doc.currency) }}</td></tr>
  </table>

  <div class="status-line">{{ status_label }}</div>

  {% if last_pe %}
  <div class="small center">Paid via {{ last_pe.mode_of_payment }}</div>
  {% endif %}

  <div class="dashed"></div>
  <div class="foot">Thank you for choosing<br>{{ doc.company }}!<br>System generated receipt.</div>
</div>
"""


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
    gym_module = frappe.db.get_value("DocType", "Gym Member", "module")
    print("Using module:", gym_module)

    # 1. Recreate the Print Format with the corrected receipt-style template
    if frappe.db.exists("Print Format", "Gym Customer Bill"):
        frappe.delete_doc("Print Format", "Gym Customer Bill", ignore_permissions=True, force=True)
    pf = frappe.get_doc({
        "doctype": "Print Format",
        "name": "Gym Customer Bill",
        "doc_type": "Sales Invoice",
        "module": gym_module,
        "standard": "No",
        "custom_format": 1,
        "print_format_type": "Jinja",
        "disabled": 0,
        "html": RECEIPT_TEMPLATE,
    })
    pf.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Recreated Print Format: Gym Customer Bill")

    # 2. Create the 'Gym Customer Receipt' log DocType (Gym Owner + System Manager only)
    if frappe.db.exists("DocType", "Gym Customer Receipt"):
        print("Gym Customer Receipt DocType already exists, skipping.")
    else:
        original_dev_mode = frappe.conf.developer_mode
        frappe.conf.developer_mode = 1
        try:
            dt = frappe.get_doc({
                "doctype": "DocType",
                "name": "Gym Customer Receipt",
                "module": gym_module,
                "custom": 0,
                "istable": 0,
                "editable_grid": 1,
                "track_changes": 1,
                "autoname": "format:RCPT-{sales_invoice}",
                "fields": [
                    {"fieldname": "sales_invoice", "fieldtype": "Link", "label": "Sales Invoice", "options": "Sales Invoice", "reqd": 1, "in_list_view": 1},
                    {"fieldname": "member", "fieldtype": "Link", "label": "Gym Member", "options": "Gym Member", "in_list_view": 1},
                    {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "in_list_view": 1},
                    {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                    {"fieldname": "generated_by", "fieldtype": "Link", "label": "Generated By", "options": "User"},
                    {"fieldname": "generated_on", "fieldtype": "Datetime", "label": "Generated On", "in_list_view": 1},
                    {"fieldname": "receipt_pdf", "fieldtype": "Attach", "label": "Receipt PDF"},
                ],
                "permissions": [
                    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
                    {"role": "Gym Owner", "read": 1, "report": 1, "export": 1, "print": 1},
                ],
            })
            dt.insert(ignore_permissions=True)
            frappe.db.commit()
            print("Created DocType: Gym Customer Receipt (Gym Owner + System Manager access only)")
        finally:
            frappe.conf.developer_mode = original_dev_mode

    # 3. api.py: add generate_and_log_receipt() + call it at the end of sell_membership()
    patch("apps/gym_management/gym_management/gym_erp_system/api.py", [
        (
'''def get_default_cash_account():''',
'''def generate_and_log_receipt(inv):
    """Render the customer receipt PDF and save a log entry against this invoice.
    Log entry access is restricted to Gym Owner + System Manager only (see DocType perms)."""
    try:
        receipt = frappe.get_doc({
            "doctype": "Gym Customer Receipt",
            "sales_invoice": inv.name,
            "member": inv.get("gym_member"),
            "amount": inv.grand_total,
            "generated_by": frappe.session.user,
            "generated_on": frappe.utils.now_datetime(),
        })
        receipt.insert(ignore_permissions=True)
        pdf_content = frappe.get_print(inv.doctype, inv.name, "Gym Customer Bill", doc=inv, as_pdf=True)
        from frappe.utils.file_manager import save_file
        file_doc = save_file(f"Receipt-{inv.name}.pdf", pdf_content, "Gym Customer Receipt", receipt.name, is_private=1)
        frappe.db.set_value("Gym Customer Receipt", receipt.name, "receipt_pdf", file_doc.file_url)
        frappe.db.commit()
    except Exception:
        frappe.log_error(title="Gym Receipt Log Failed", message=frappe.get_traceback())


def get_default_cash_account():'''
        ),
        (
'''    inv.reload()
    return {
        "member": member, "invoice": inv.name, "grand_total": inv.grand_total,
        "outstanding_amount": inv.outstanding_amount, "due_date": inv.due_date,
        "payment_entry": payment_entry,
    }''',
'''    inv.reload()
    generate_and_log_receipt(inv)
    return {
        "member": member, "invoice": inv.name, "grand_total": inv.grand_total,
        "outstanding_amount": inv.outstanding_amount, "due_date": inv.due_date,
        "payment_entry": payment_entry,
    }'''
        ),
    ])

    # 4. gym_subscription.py: also log a receipt for auto-renewed invoices
    patch("apps/gym_management/gym_management/gym_erp_system/gym_subscription.py", [
        (
'''    frappe.db.commit()
    send_auto_renew_email(member.name, plan.plan_name, inv.name, new_end_date, inv.grand_total, inv.due_date)
    return True''',
'''    frappe.db.commit()
    from gym_management.gym_erp_system.api import generate_and_log_receipt
    generate_and_log_receipt(inv)
    send_auto_renew_email(member.name, plan.plan_name, inv.name, new_end_date, inv.grand_total, inv.due_date)
    return True'''
        ),
    ])

    frappe.clear_cache()
    print("DONE")
