import frappe
def run():
    print("Website Settings doctype exists:", frappe.db.exists("DocType", "Website Settings"))
    rows = frappe.db.sql("""SELECT parent, fieldname, label FROM `tabDocField` WHERE fieldname LIKE '%favicon%' OR label LIKE '%Favicon%'""", as_dict=True)
    print("Favicon fields found:")
    for r in rows:
        print(" ", r)
    rows2 = frappe.db.sql("""SELECT parent, fieldname, label FROM `tabDocField` WHERE fieldname IN ('app_name','app_title') OR label LIKE '%App Name%' OR label LIKE '%App Title%'""", as_dict=True)
    print("App name/title fields found:")
    for r in rows2:
        print(" ", r)
