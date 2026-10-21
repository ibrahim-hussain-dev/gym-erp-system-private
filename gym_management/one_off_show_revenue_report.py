import frappe
import subprocess

def run():
    print("=" * 60)
    print("REPORT DOCTYPE RECORD: Gym Revenue By Plan")
    print("=" * 60)
    if frappe.db.exists("Report", "Gym Revenue By Plan"):
        doc = frappe.get_doc("Report", "Gym Revenue By Plan")
        print(f"report_type: {doc.report_type}")
        print(f"is_standard: {doc.is_standard}")
        print(f"module: {doc.module}")
        print(f"ref_doctype: {doc.ref_doctype}")
        print()
        print("QUERY (if Query Report):")
        print(doc.query or "(none — likely a Script Report instead)")
    else:
        print("NOT FOUND under that exact name — searching similar...")
        similar = frappe.get_all("Report", filters={"report_name": ["like", "%Revenue%"]}, fields=["name", "report_type", "module"])
        print(similar)

    print()
    print("=" * 60)
    print("FILES ON DISK")
    print("=" * 60)
    out = subprocess.run(["find", "/home/frappe/frappe-bench/apps/gym_management", "-ipath", "*report*revenue*"], capture_output=True, text=True)
    print(out.stdout)

    print()
    print("=" * 60)
    print("FILE CONTENTS")
    print("=" * 60)
    for f in out.stdout.strip().split("\n"):
        if f and (f.endswith(".py") or f.endswith(".js") or f.endswith(".json")):
            print(f"--- {f} ---")
            print(subprocess.run(["cat", f], capture_output=True, text=True).stdout)
            print()
