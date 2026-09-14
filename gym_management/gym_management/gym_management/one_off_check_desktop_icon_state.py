import frappe
import json

def run():
    seen = set()
    all_rows = []
    for pattern in ["%Impact%", "%Gym%"]:
        rows = frappe.get_all("Desktop Icon", filters={"label": ["like", pattern]}, fields=["name"])
        all_rows.extend(rows)

    for r in all_rows:
        if r["name"] in seen:
            continue
        seen.add(r["name"])
        doc = frappe.get_doc("Desktop Icon", r["name"])
        print(json.dumps(doc.as_dict(), indent=2, default=str))
        print("---")

    print("\n=== Navbar logo (uploaded via UI) ===")
    print("app_logo:", frappe.db.get_single_value("Navbar Settings", "app_logo"))
