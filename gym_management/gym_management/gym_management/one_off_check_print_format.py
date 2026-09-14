import frappe

def run():
    if not frappe.db.exists("Print Format", "Gym Customer Bill"):
        print("Print Format 'Gym Customer Bill' not found in DB.")
        return
    pf = frappe.get_doc("Print Format", "Gym Customer Bill")
    print("=== Print Format meta ===")
    print("doc_type:", pf.doc_type)
    print("print_format_type:", pf.print_format_type)
    print("standard:", pf.standard)
    print("disabled:", pf.disabled)
    print("css length:", len(pf.css or ""))
    print("html length:", len(pf.html or ""))
    print("")
    print("=== CSS ===")
    print(pf.css or "(none)")
    print("")
    print("=== HTML ===")
    print(pf.html or "(none)")
