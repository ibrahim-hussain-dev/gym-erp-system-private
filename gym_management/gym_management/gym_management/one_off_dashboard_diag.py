import frappe
import subprocess
import json

BENCH = "/home/frappe/frappe-bench/"
PKG = BENCH + "apps/gym_management/gym_management/"


def grep(term):
    try:
        out = subprocess.run(["grep", "-rn", term, PKG], capture_output=True, text=True)
        return out.stdout or "(no matches)"
    except Exception as e:
        return f"grep failed: {e}"


def run():
    print("=" * 70)
    print("STEP 0: grep source for 'Outstanding' / 'Cash Collected' / 'NaN'")
    print("=" * 70)
    for term in ["Outstanding", "Cash Collected", "outstanding_receivable", "cash_collected"]:
        print(f"--- grep: {term} ---")
        print(grep(term))

    print("=" * 70)
    print("STEP 1: all Number Card docs (name/label/type/doctype/function/filters)")
    print("=" * 70)
    cards = frappe.get_all(
        "Number Card",
        fields=["name", "label", "document_type", "type", "function", "aggregate_function_based_on", "filters_json", "is_public", "report_name"],
    )
    for c in cards:
        print(c)

    print("=" * 70)
    print("STEP 2: Workspace 'Impact Health Studio' content blocks (number_card/chart/card)")
    print("=" * 70)
    if frappe.db.exists("Workspace", "Impact Health Studio"):
        ws = frappe.get_doc("Workspace", "Impact Health Studio")
        try:
            content = json.loads(ws.content or "[]")
        except Exception:
            content = []
        for block in content:
            if block.get("type") in ("number_card", "chart", "card", "shortcut"):
                print(block)
        print("--- ws.number_cards child table (if any) ---")
        if hasattr(ws, "number_cards"):
            for nc in ws.number_cards:
                print(nc.as_dict())
        print("--- ws.charts child table (if any) ---")
        if hasattr(ws, "charts"):
            for ch in ws.charts:
                print(ch.as_dict())
    else:
        print("Workspace 'Impact Health Studio' not found")

    print("=" * 70)
    print("STEP 3: report modules under gym_erp_system/report/")
    print("=" * 70)
    reports = frappe.get_all("Report", filters={"module": ["like", "%Gym%"]}, fields=["name", "report_type", "ref_doctype", "is_standard"])
    for r in reports:
        print(r)

    print("=" * 70)
    print("STEP 4: contents of Gym Revenue-related report .py files")
    print("=" * 70)
    try:
        out = subprocess.run(["find", PKG + "gym_erp_system/report/", "-name", "*.py"], capture_output=True, text=True)
        files = [f for f in out.stdout.splitlines() if f.strip()]
        print("Found report python files:", files)
        for f in files:
            if "revenue" in f.lower() or "outstanding" in f.lower() or "cash" in f.lower():
                print(f"--- {f} ---")
                with open(f) as fh:
                    print(fh.read())
    except Exception as e:
        print("find/read failed:", e)

    print("DONE.")
