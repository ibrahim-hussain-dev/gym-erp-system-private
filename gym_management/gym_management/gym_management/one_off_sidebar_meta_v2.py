import frappe
import json

def run():
	meta = frappe.get_meta("Workspace Sidebar Item")
	skip_types = {"Section Break", "Column Break", "Tab Break"}
	fields = [f.fieldname for f in meta.fields if f.fieldtype not in skip_types]
	print("FIELDS:", fields)

	rows = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Gym Operations"},
		fields=["name", "idx"] + fields,
		order_by="idx asc",
	)
	print("ROW COUNT:", len(rows))
	for r in rows:
		print(json.dumps(r, default=str))
