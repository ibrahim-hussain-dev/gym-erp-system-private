import frappe


def run():
    print("=" * 80)
    print("STEP 1: 'Sell Membership' Page record (a known-working sidebar item)")
    print("=" * 80)
    if frappe.db.exists("Page", "sell-membership"):
        doc = frappe.get_doc("Page", "sell-membership")
        print(doc.as_dict())
    else:
        # try by title/name search
        pages = frappe.get_all("Page", filters={"name": ["like", "%sell%"]}, fields=["name", "title", "module", "page_name", "standard", "system_page"])
        print("  not found by exact name, search results:", pages)

    print()
    print("=" * 80)
    print("STEP 2: ALL Page records with module = 'Gym Erp System' (or similar)")
    print("=" * 80)
    modules = frappe.get_all("Module Def", filters={"app_name": "gym_management"}, fields=["name"])
    print("  modules for gym_management app:", modules)
    for m in modules:
        pages = frappe.get_all("Page", filters={"module": m.name}, fields=["name", "title", "page_name", "module"])
        print(f"  Pages in module '{m.name}':", pages)

    print()
    print("=" * 80)
    print("STEP 3: does a 'Sales Invoice' Page record already exist anywhere?")
    print("=" * 80)
    existing = frappe.get_all("Page", filters={"name": ["like", "%sales%invoice%"]}, fields=["name", "title", "module"])
    print("  ", existing)

    print()
    print("DONE.")
