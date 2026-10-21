import frappe

TEMPLATE = """
<style>
  .print-format {
    page-width: 80mm;
    page-height: {{ 100 + (doc.items|length * 15) }}mm;
    margin-top: 4mm;
    margin-bottom: 4mm;
    margin-left: 3mm;
    margin-right: 3mm;
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

def run():
	pf = frappe.get_doc("Print Format", "Gym Customer Bill")
	pf.html = TEMPLATE
	pf.save(ignore_permissions=True)
	frappe.db.commit()
	print("UPDATED:", pf.name)
