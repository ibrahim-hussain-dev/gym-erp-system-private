import frappe
import json

def run():
	columns = frappe.db.get_table_columns("Workspace Sidebar Item")
	print("COLUMNS:", columns)

	rows = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Gym Operations"},
		fields=columns,
		order_by="idx asc",
	)
	print("ROW COUNT:", len(rows))
	for r in rows:
		print(json.dumps(r, default=str))
