import frappe
import json

def run():
	meta = frappe.get_meta("Workspace Sidebar Item")
	fields = [f.fieldname for f in meta.fields]
	print("FIELDS:", fields)

	rows = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Gym Operations"},
		fields=fields,
		order_by="idx asc",
	)
	print("ROW COUNT:", len(rows))
	for r in rows:
		print(json.dumps(r, default=str))
