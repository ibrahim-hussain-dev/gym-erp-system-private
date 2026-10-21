import frappe

TEMPLATE = """
<style>
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .bill-doc { font-family: 'Segoe UI', Arial, sans-serif; color: #223; max-width: 780px; margin: 0 auto; border: 1px solid #e3e8e7; border-radius: 10px; overflow: hidden; }
  .bill-band { background: linear-gradient(135deg, #0F9B8E, #0b7a70); color: #fff; padding: 26px 32px; display: flex; justify-content: space-between; align-items: flex-start; }
  .bill-company { font-size: 22px; font-weight: 700; letter-spacing: 0.3px; }
  .bill-sub { font-size: 12.5px; color: rgba(255,255,255,0.85); margin-top: 2px; }
  .bill-meta { text-align: right; font-size: 12px; line-height: 1.7; }
  .bill-meta b { font-weight: 600; }
  .status-pill { display: inline-block; margin-top: 8px; padding: 4px 14px; border-radius: 20px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.5px; color: #fff; }
  .status-paid { background: #1f8a6f; }
  .status-partial { background: #d98426; }
  .status-unpaid { background: #c94a3a; }
  .bill-body { padding: 26px 32px; background: #fff; }
  .bill-to-card { background: #f4f9f8; border: 1px solid #e5efed; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px; font-size: 13px; line-height: 1.7; }
  .bill-to-card .label { color: #6b8985; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  table.bill-table { width: 100%; border-collapse: collapse; margin-top: 4px; }
  table.bill-table thead th { background: #e8f6f4; color: #0c6e63; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.4px; padding: 10px 10px; text-align: left; border-bottom: 2px solid #cdeae5; }
  table.bill-table tbody td { padding: 10px; font-size: 13px; border-bottom: 1px solid #eef2f1; }
  table.bill-table tbody tr:nth-child(even) { background: #fafcfc; }
  .totals-card { margin-top: 18px; margin-left: auto; width: 300px; border: 1px solid #e5efed; border-radius: 8px; overflow: hidden; }
  .totals-card .trow { display: flex; justify-content: space-between; padding: 8px 16px; font-size: 13px; }
  .totals-card .trow.grand { background: #f4f9f8; font-weight: 700; font-size: 15.5px; border-top: 1px solid #dcece9; border-bottom: 1px solid #dcece9; }
  .totals-card .trow.paid span:last-child { color: #1f8a6f; font-weight: 600; }
  .totals-card .trow.due span:last-child { color: #c94a3a; font-weight: 700; }
  .payment-note { margin-top: 16px; background: #fbfaf3; border: 1px solid #f0ecd6; border-radius: 6px; padding: 10px 14px; font-size: 12px; color: #6b6248; }
  .bill-footer { text-align: center; padding: 18px 20px 22px; font-size: 11.5px; color: #9aa5a3; border-top: 1px dashed #e5efed; }
  .bill-footer .thanks { font-size: 13px; color: #445; margin-bottom: 4px; font-weight: 600; }
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

<div class="bill-doc">
  <div class="bill-band">
    <div>
      <div class="bill-company">{{ doc.company }}</div>
      <div class="bill-sub">Customer Bill / Payment Receipt</div>
    </div>
    <div class="bill-meta">
      <div><b>Bill No:</b> {{ doc.name }}</div>
      <div><b>Generated On:</b> {{ frappe.utils.format_datetime(doc.creation, "dd MMM yyyy, hh:mm a") }}</div>
      {% if last_pe %}<div><b>Payment Time:</b> {{ frappe.utils.format_datetime(last_pe.creation, "dd MMM yyyy, hh:mm a") }}</div>{% endif %}
      <span class="status-pill {{ status_class }}">{{ status_label }}</span>
    </div>
  </div>

  <div class="bill-body">
    <div class="bill-to-card">
      <div class="label">Bill To</div>
      <div style="font-size:14.5px; font-weight:600;">{{ member_info.full_name if member_info else doc.customer_name }}</div>
      {% if member_info %}
        {% if member_info.phone %}<div>Phone: {{ member_info.phone }}</div>{% endif %}
        {% if member_info.email %}<div>Email: {{ member_info.email }}</div>{% endif %}
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

    <div class="totals-card">
      <div class="trow"><span>Sub Total</span><span>{{ frappe.utils.fmt_money(doc.net_total, currency=doc.currency) }}</span></div>
      {% if doc.discount_amount %}
      <div class="trow"><span>Discount{% if doc.additional_discount_percentage %} ({{ doc.additional_discount_percentage }}%){% endif %}</span><span>- {{ frappe.utils.fmt_money(doc.discount_amount, currency=doc.currency) }}</span></div>
      {% endif %}
      <div class="trow grand"><span>Grand Total</span><span>{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</span></div>
      <div class="trow paid"><span>Paid</span><span>{{ frappe.utils.fmt_money(paid_amount, currency=doc.currency) }}</span></div>
      <div class="trow due"><span>Balance Due</span><span>{{ frappe.utils.fmt_money(doc.outstanding_amount, currency=doc.currency) }}</span></div>
    </div>

    {% if last_pe %}
    <div class="payment-note">
      Last payment of {{ frappe.utils.fmt_money(last_pe.paid_amount, currency=doc.currency) }} received via <b>{{ last_pe.mode_of_payment }}</b> on {{ frappe.utils.format_datetime(last_pe.creation, "dd MMM yyyy, hh:mm a") }}.
    </div>
    {% endif %}
  </div>

  <div class="bill-footer">
    <div class="thanks">Thank you for choosing {{ doc.company }}!</div>
    This is a system-generated receipt. Please retain it for your records.
  </div>
</div>
"""

def run():
	pf = frappe.get_doc("Print Format", "Gym Customer Bill")
	pf.html = TEMPLATE
	pf.save(ignore_permissions=True)
	frappe.db.commit()
	print("UPDATED:", pf.name)
