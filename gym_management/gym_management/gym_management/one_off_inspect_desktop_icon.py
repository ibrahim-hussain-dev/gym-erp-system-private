import frappe
import json

def run():
    meta = frappe.get_meta("Desktop Icon")
    print("=== FIELDS ===")
    for df in meta.fields:
        print(df.fieldname, "|", df.fieldtype, "|", "MANDATORY" if df.reqd else "optional")

    print("\n=== TOTAL COUNT ===")
    print(frappe.db.count("Desktop Icon"))

    print("\n=== SAMPLE ROWS (first 8, standard=1) ===")
    rows = frappe.get_all("Desktop Icon", filters={"standard": 1}, fields=["name"], limit=8)
    for r in rows:
        doc = frappe.get_doc("Desktop Icon", r.name)
        print(json.dumps(doc.as_dict(), indent=2, default=str))
        print("---")

    print("\n=== SAMPLE ROWS (first 5, standard=0 i.e. custom/app-created) ===")
    rows2 = frappe.get_all("Desktop Icon", filters={"standard": 0}, fields=["name"], limit=5)
    for r in rows2:
        doc = frappe.get_doc("Desktop Icon", r.name)
        print(json.dumps(doc.as_dict(), indent=2, default=str))
        print("---")
