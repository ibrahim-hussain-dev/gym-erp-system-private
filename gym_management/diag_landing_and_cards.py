import frappe


def run():
    print("=" * 80)
    print("STEP 1: home_page field for fd1/owner (can override default_workspace on login)")
    print("=" * 80)
    for u in ["fd1@gym.local", "owner@gym.local"]:
        if frappe.db.exists("User", u):
            hp = frappe.db.get_value("User", u, "home_page")
            print(f"  {u}: home_page={hp!r}")

    print()
    print("=" * 80)
    print("STEP 2: System Settings 'home_page' (global default) + Website Settings 'home_page'")
    print("=" * 80)
    ss_home = frappe.db.get_single_value("System Settings", "home_page") if frappe.db.exists("DocType", "System Settings") else None
    print(f"  System Settings.home_page = {ss_home}")
    try:
        ws_home = frappe.db.get_single_value("Website Settings", "home_page")
        print(f"  Website Settings.home_page = {ws_home}")
    except Exception as e:
        print("  (no home_page field on Website Settings)", e)

    print()
    print("=" * 80)
    print("STEP 3: ALL Number Card records referenced by our workspaces (no module filter)")
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
    print("DONE.")
