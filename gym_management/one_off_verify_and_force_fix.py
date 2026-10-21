import frappe
import re

def run():
	pf = frappe.get_doc("Print Format", "Gym Customer Bill")
	has_page_size = "page-size" in pf.html
	print("Current html has 'page-size':", has_page_size)

	# force-remove any page-size line no matter the exact formatting
	new_html = re.sub(r'\n\s*page-size\s*:\s*[^;]+;', '', pf.html)
	changed = new_html != pf.html
	print("Did regex find and remove a page-size line:", changed)

	if changed:
		pf.html = new_html
		pf.save(ignore_permissions=True)
		frappe.db.commit()
		print("SAVED - page-size line removed for real this time.")
	else:
		print("Nothing to remove - page-size was already absent.")
