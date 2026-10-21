import frappe

TEMPLATE = """
<style>
  .bill-wrap { font-family: sans-serif; color: #222; }
  .bill-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px; }
  .bill-title { font-size: 20px; font-weight: bold; }
  .bill-sub { color: #666; font-size: 12px; }
  table.bill-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  table.bill-table th, table.bill-table td { border-bottom: 1px solid #ddd; padding: 6px 8px; text-align: left; font-size: 12px; }
  table.bill-table th { background: #f5f5f5; }
  .totals-row td { border: none; padding: 3px 8px; font-size: 13px; }
  .totals-row.grand td { font-weight: bold; font-size: 15px; border-top: 1px solid #333; }
  .status-badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; color: #fff; }
  .status-paid { background: #0F9B8E; }
  .status-partial { background: #E4972E; }
  .status-unpaid { background: #E4572E; }
</style>

{% set paid_amount = doc.grand_total - doc.outstanding_amount %}
{% set pe_rows = frappe.get_all("Payment Entry Reference", filters={"reference_doctype": "Sales Invoice", "reference_name": doc.name}, fields=["parent"], order_by="creation desc", limit_page_length=1) %}
{% set last_pe = frappe.get_doc("Payment Entry", pe_rows[0].parent) if pe_rows else None %}
{% set member_info = frappe.db.get_value("Gym Member", doc.gym_member, ["full_name", "phone", "email"], as_dict=True) if doc.get("gym_member") else None %}
{% if doc.outstanding_amount <= 0 %}
  {% set status_label, status_class = "PAID", "status-paid" %}
{% elif paid_amount > 0 %}
  {% set status_label, status_class = "PARTLY PAID", "status-partial" %}
{% else %}
  {% set status_label, status_class = "UNPAID", "status-unpaid" %}
{% endif %}

<div class="bill-wrap">
  <div class="bill-header">
    <div>
      <div class="bill-title">{{ doc.company }}</div>
      <div class="bill-sub">Customer Bill / Payment Receipt</div>
    </div>
    <div style="text-align:right;">
      <div><b>Bill No:</b> {{ doc.name }}</div>
      <div><b>Bill Date:</b> {{ frappe.utils.formatdate(doc.posting_date) }}</div>
      {% if last_pe %}<div><b>Payment Date:</b> {{ frappe.utils.formatdate(last_pe.posting_date) }}</div>{% endif %}
      <div style="margin-top:6px;"><span class="status-badge {{ status_class }}">{{ status_label }}</span></div>
    </div>
  </div>

  <div style="margin-bottom:14px;">
    <b>Bill To:</b> {{ member_info.full_name if member_info else doc.customer_name }}<br>
    {% if member_info %}
      {% if member_info.phone %}Phone: {{ member_info.phone }}<br>{% endif %}
      {% if member_info.email %}Email: {{ member_info.email }}<br>{% endif %}
    {% endif %}
  </div>

  <table class="bill-table">
    <thead>
      <tr><th>#</th><th>Item</th><th>Qty</th><th>Rate</th><th>Discount</th><th style="text-align:right;">Amount</th></tr>
    </thead>
    <tbody>
      {% for item in doc.items %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ item.item_name }}</td>
        <td>{{ item.qty }}</td>
        <td>{{ frappe.utils.fmt_money(item.price_list_rate or item.rate, currency=doc.currency) }}</td>
        <td>
          {% if item.discount_percentage %}{{ item.discount_percentage }}%
          {% elif item.discount_amount %}{{ frappe.utils.fmt_money(item.discount_amount, currency=doc.currency) }}
          {% else %}-{% endif %}
        </td>
        <td style="text-align:right;">{{ frappe.utils.fmt_money(item.amount, currency=doc.currency) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table style="width:100%; margin-top:10px;">
    <tr class="totals-row"><td style="text-align:right;" colspan="5">Sub Total</td><td style="text-align:right;">{{ frappe.utils.fmt_money(doc.net_total, currency=doc.currency) }}</td></tr>
    {% if doc.discount_amount %}
    <tr class="totals-row"><td style="text-align:right;" colspan="5">Discount {% if doc.additional_discount_percentage %}({{ doc.additional_discount_percentage }}%){% endif %}</td><td style="text-align:right;">- {{ frappe.utils.fmt_money(doc.discount_amount, currency=doc.currency) }}</td></tr>
    {% endif %}
    <tr class="totals-row grand"><td style="text-align:right;" colspan="5">Grand Total</td><td style="text-align:right;">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
    <tr class="totals-row"><td style="text-align:right;" colspan="5">Paid</td><td style="text-align:right; color:#0F9B8E;">{{ frappe.utils.fmt_money(paid_amount, currency=doc.currency) }}</td></tr>
    <tr class="totals-row"><td style="text-align:right;" colspan="5">Balance Due</td><td style="text-align:right; color:#E4572E;">{{ frappe.utils.fmt_money(doc.outstanding_amount, currency=doc.currency) }}</td></tr>
  </table>

  {% if last_pe %}
  <div style="margin-top:14px; font-size:12px; color:#555;">
    Last Payment: {{ frappe.utils.fmt_money(last_pe.paid_amount, currency=doc.currency) }} via {{ last_pe.mode_of_payment }} on {{ frappe.utils.formatdate(last_pe.posting_date) }}
  </div>
  {% endif %}

  <div style="margin-top:20px; font-size:11px; color:#999;">Thank you for choosing {{ doc.company }}.</div>
</div>
"""

def run():
	if frappe.db.exists("Print Format", "Gym Customer Bill"):
		frappe.delete_doc("Print Format", "Gym Customer Bill", ignore_permissions=True, force=True)

	pf = frappe.get_doc({
		"doctype": "Print Format",
		"name": "Gym Customer Bill",
		"doc_type": "Sales Invoice",
		"module": "Gym-ERP-System",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "Jinja",
		"disabled": 0,
		"html": TEMPLATE,
	})
	pf.insert(ignore_permissions=True)
	frappe.db.commit()
	print("CREATED:", pf.name)
