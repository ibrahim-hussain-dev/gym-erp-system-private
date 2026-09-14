import frappe

def run():
    print("=== Desktop Icon rows matching 'Gym' ===")
    rows = frappe.get_all(
        "Desktop Icon",
        filters={"label": ["like", "%Gym%"]},
        fields=["name", "label", "icon", "logo_url", "app", "hidden", "standard"]
    )
    for r in rows:
        print(r)

    also_by_app = frappe.get_all(
        "Desktop Icon",
        filters={"app": "gym_management"},
        fields=["name", "label", "icon", "logo_url", "app", "hidden", "standard"]
    )
    print("\n=== Desktop Icon rows with app=gym_management ===")
    for r in also_by_app:
        print(r)

    print("\n=== Navbar logo (uploaded via UI) ===")
    logo_url = frappe.db.get_single_value("Navbar Settings", "app_logo")
    print("app_logo:", logo_url)

    target = None
    for r in (rows + also_by_app):
        if r["label"] == "Gym Operations" or r["app"] == "gym_management":
            target = r["name"]
            break

    if target and logo_url:
        doc = frappe.get_doc("Desktop Icon", target)
        doc.logo_url = logo_url
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"\nUpdated Desktop Icon '{target}' -> logo_url = {logo_url}")
    else:
        print("\nCould NOT auto-update. target=", target, "| logo_url=", logo_url)
        print("Paste this full output back so we can fix manually.")

    frappe.clear_cache()
    print("\nDONE")
