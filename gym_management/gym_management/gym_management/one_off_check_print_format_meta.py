import frappe

def run():
    meta = frappe.get_meta("Print Format")
    for f in meta.fields:
        if "page" in f.fieldname.lower() or "size" in f.fieldname.lower():
            print(f.fieldname, "|", f.fieldtype, "|", f.label, "|", f.options)
