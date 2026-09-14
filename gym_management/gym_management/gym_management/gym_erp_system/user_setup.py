import frappe

GYM_ROLES = {"Gym Front Desk", "Gym Trainer", "Gym Manager"}


def set_default_workspace_for_gym_user(doc, method):
	"""Auto-land gym staff on the Gym Operations workspace after login,
	instead of the default cluttered Frappe home screen."""
	try:
		user_roles = {r.role for r in doc.roles}
		if user_roles & GYM_ROLES and doc.default_workspace != "Gym Operations":
			doc.db_set("default_workspace", "Gym Operations", update_modified=False)
	except Exception:
		frappe.log_error(title="Gym Default Workspace Hook Failed", message=frappe.get_traceback())
