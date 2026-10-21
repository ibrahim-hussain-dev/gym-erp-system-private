import frappe
import json

def run():
	# 1) Sales Invoice relevant fields
	meta = frappe.get_meta("Sales Invoice")
	interesting = [
		"outstanding_amount", "paid_amount", "advance_paid", "is_pos",
		"discount_amount", "additional_discount_percentage", "apply_discount_on",
		"posting_date", "due_date", "grand_total", "net_total",
	]
	print("SALES INVOICE FIELDS PRESENT:")
	for f in interesting:
		field = meta.get_field(f)
		print(f"  {f}: {'YES - ' + field.fieldtype if field else 'NOT A FIELD (may be a property, e.g. computed)'}")

	# 2) Look at one real recent invoice to see actual values
	inv_name = frappe.db.get_value("Sales Invoice", {"customer": "Utbah"}, "name", order_by="creation desc")
	if inv_name:
		inv = frappe.get_doc("Sales Invoice", inv_name)
		print("\nSAMPLE INVOICE:", inv_name)
		for f in interesting:
			print(f"  {f} = {inv.get(f)}")
		print("  items:", [{"item": d.item_name, "qty": d.qty, "rate": d.rate, "amount": d.amount} for d in inv.items])

		# 3) Find any linked Payment Entry (via Payment Entry Reference)
		pe_refs = frappe.get_all(
			"Payment Entry Reference",
			filters={"reference_doctype": "Sales Invoice", "reference_name": inv_name},
			fields=["parent", "allocated_amount"],
		)
		print("  linked Payment Entries:", pe_refs)
		for ref in pe_refs:
			pe_date = frappe.db.get_value("Payment Entry", ref["parent"], "posting_date")
			print(f"    {ref['parent']} posting_date={pe_date} allocated={ref['allocated_amount']}")

	# 4) Existing print formats for Sales Invoice
	pf = frappe.get_all("Print Format", filters={"doc_type": "Sales Invoice"}, fields=["name", "standard", "disabled"])
	print("\nEXISTING PRINT FORMATS FOR Sales Invoice:", pf)

	default_pf = frappe.db.get_value("Property Setter", {"doc_type": "Sales Invoice", "property": "default_print_format"}, "value")
	print("DEFAULT PRINT FORMAT (property setter):", default_pf)
