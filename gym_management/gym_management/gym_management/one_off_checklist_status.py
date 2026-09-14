import frappe

def run():
	print("========== GYM MEMBER FIELDS ==========")
	member_fields = [f.fieldname for f in frappe.get_meta("Gym Member").fields]
	print(member_fields)
	for check in ["activity_level", "ladies_hours", "workout_history", "registration_tenure"]:
		print(f"  has '{check}':", check in member_fields)

	print("\n========== GYM INVOICE DOCTYPE ==========")
	exists = frappe.db.exists("DocType", "Gym Invoice")
	print("Gym Invoice doctype exists:", bool(exists))
	if exists:
		inv_fields = [f.fieldname for f in frappe.get_meta("Gym Invoice").fields]
		print("Fields:", inv_fields)
		sample = frappe.get_all("Gym Invoice", fields=["name", "grand_total", "paid_amount", "remaining_amount", "status"], limit_page_length=3, order_by="creation desc")
		print("Sample records:", sample)

	print("\n========== GYM PLAN GROUPING ==========")
	plan_fields = [f.fieldname for f in frappe.get_meta("Gym Plan").fields]
	print(plan_fields)
	for check in ["plan_group", "plan_type", "category"]:
		print(f"  has '{check}':", check in plan_fields)

	print("\n========== GYM TRAINER SALARY/COMMISSION ==========")
	trainer_fields = [f.fieldname for f in frappe.get_meta("Gym Trainer").fields]
	print(trainer_fields)
	for check in ["salary", "base_salary", "commission_percentage"]:
		print(f"  has '{check}':", check in trainer_fields)

	print("\n========== EXPENSE REPORT ==========")
	reports = frappe.get_all("Report", filters={"ref_doctype": "Gym Expense"}, fields=["name"])
	print("Reports on Gym Expense:", reports)
