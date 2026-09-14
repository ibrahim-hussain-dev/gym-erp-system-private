import frappe

def run():
	logs = frappe.get_all(
		"Error Log",
		filters={"method": ["like", "%download_pdf%"]},
		fields=["name", "creation", "error"],
		order_by="creation desc",
		limit_page_length=3,
	)
	if not logs:
		logs = frappe.get_all(
			"Error Log",
			fields=["name", "creation", "error"],
			order_by="creation desc",
			limit_page_length=3,
		)
	for log in logs:
		print("=====", log.name, log.creation, "=====")
		print(log.error)
		print()
