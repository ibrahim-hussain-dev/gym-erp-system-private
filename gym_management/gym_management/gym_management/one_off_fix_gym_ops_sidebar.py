import frappe

def run():
	doc = frappe.get_doc("Workspace Sidebar", "Gym Operations")

	# Sanity scan: report any OTHER broken links we haven't already identified
	exists_check = {"Page": "Page", "DocType": "DocType", "Report": "Report", "Workspace": "Workspace"}
	print("--- Scanning all items for broken links ---")
	for row in doc.items:
		if row.type == "Link" and row.link_to and row.link_type in exists_check:
			if not frappe.db.exists(exists_check[row.link_type], row.link_to):
				print(f"BROKEN: idx={row.idx} name={row.name} label={row.label!r} link_type={row.link_type} link_to={row.link_to!r}")
	print("--- Scan done ---")

	remove_names = {
		"4md7c1hudn",  # Freeze/Resume Mmbership -> manage-subscription (deleted page)
		"4md334jm7r",  # (no label) -> Gym Membership Retention (deleted report)
		"4mdvoqqf72",  # Gym Membership Retention -> deleted report
		"4mdkha6t10",  # Gym Membership Retention (dup) -> deleted report
		"4mdupgpm3l",  # Membership Retention -> deleted report
	}

	before = len(doc.items)
	doc.items = [row for row in doc.items if row.name not in remove_names]
	after_remove = len(doc.items)

	doc.append("items", {
		"type": "Link",
		"link_type": "Report",
		"link_to": "Gym Member Retention",
		"label": "Member Retention",
		"icon": "table",
		"collapsible": 1,
	})

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	print("BEFORE:", before, "AFTER REMOVE:", after_remove, "AFTER ADD:", len(doc.items))
