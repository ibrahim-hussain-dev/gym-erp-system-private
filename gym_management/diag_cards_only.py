import frappe


def run():
    print("=" * 80)
    print("STEP 1: System Settings 'home_page' (global default, if field exists)")
    print("=" * 80)
    try:
        ss_home = frappe.db.get_single_value("System Settings", "home_page")
        print(f"  System Settings.home_page = {ss_home}")
    except Exception as e:
        print("  (no such field)", e)

    print()
    print("=" * 80)
    print("STEP 2: ALL Number Card records referenced by our workspaces")
    print("=" * 80)
    names = [
        "Today's Check-ins", "Active Memberships",
        "Total Outstanding Receivables", "Today's Cash Collected",
    ]
    for n in names:
        if frappe.db.exists("Number Card", n):
            doc = frappe.get_doc("Number Card", n)
            print(f"  --- {n} ---")
            print("   ", {
                "document_type": doc.document_type,
                "function": doc.function,
                "aggregate_function_based_on": doc.aggregate_function_based_on,
                "filters_json": doc.filters_json,
                "module": doc.module,
                "is_public": doc.is_public,
            })
        else:
            print(f"  '{n}' NOT FOUND as Number Card")

    print()
    print("=" * 80)
    print("STEP 3: Front Desk role - permission on Gym Member (for a 'Total Members' style card)")
    print("=" * 80)
    rows = frappe.get_all(
        "Custom DocPerm",
        filters={"parent": "Gym Member", "role": "Gym Front Desk"},
        fields=["read", "write", "create", "report"],
    )
    print("  ", rows)

    print()
    print("DONE.")
