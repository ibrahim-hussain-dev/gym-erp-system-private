import frappe

def run():
    if not frappe.db.exists("Gym Branch", "Main Branch"):
        frappe.get_doc({"doctype": "Gym Branch", "branch_name": "Main Branch"}).insert(ignore_permissions=True)
        print("Created Gym Branch: Main Branch")

    if not frappe.db.exists("Custom Field", {"dt": "Gym Member", "fieldname": "branch"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Gym Member",
            "fieldname": "branch",
            "label": "Branch",
            "fieldtype": "Link",
            "options": "Gym Branch",
            "insert_after": "full_name",
        }).insert(ignore_permissions=True)
        print("Created Custom Field: Gym Member.branch")

    frappe.db.commit()
    frappe.db.sql("update `tabGym Member` set branch = %s where branch is null or branch = ''", ("Main Branch",))
    frappe.db.commit()
    print("Backfilled existing members with Main Branch")
