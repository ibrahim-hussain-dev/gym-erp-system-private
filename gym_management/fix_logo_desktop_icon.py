import frappe

CORRECT_LOGO_URL = "/files/impact_logo_512.png"


def run():
    # 1. Fix existing "Impact Health Studio" Desktop Icon logo_url
    #    (currently pointing at the private, non-public copy of the file,
    #    which returns 403 in the browser)
    doc = frappe.get_doc("Desktop Icon", "Impact Health Studio")
    old_logo_url = doc.logo_url
    if old_logo_url != CORRECT_LOGO_URL:
        doc.logo_url = CORRECT_LOGO_URL
        doc.save(ignore_permissions=True)
        print(f"Impact Health Studio: logo_url changed {old_logo_url!r} -> {CORRECT_LOGO_URL!r}")
    else:
        print("Impact Health Studio: logo_url already correct, no change needed")

    # 2. Create/ensure "Front Desk" Desktop Icon exists with the same logo,
    #    mirroring the structure of the Impact Health Studio record
    #    (Front Desk currently has no Desktop Icon record at all, which is
    #    why no logo shows there)
    if frappe.db.exists("Desktop Icon", "Front Desk"):
        fd_doc = frappe.get_doc("Desktop Icon", "Front Desk")
        old_fd_logo = fd_doc.logo_url
        if old_fd_logo != CORRECT_LOGO_URL:
            fd_doc.logo_url = CORRECT_LOGO_URL
            fd_doc.save(ignore_permissions=True)
            print(f"Front Desk: logo_url changed {old_fd_logo!r} -> {CORRECT_LOGO_URL!r}")
        else:
            print("Front Desk: logo_url already correct, no change needed")
    else:
        new_doc = frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": "Front Desk",
                "icon_type": "Link",
                "link_type": "Workspace Sidebar",
                "link_to": "Front Desk",
                "standard": 0,
                "app": "gym_management",
                "logo_url": CORRECT_LOGO_URL,
                "bg_color": "blue",
                "hidden": 0,
                "restrict_removal": 0,
            }
        )
        new_doc.insert(ignore_permissions=True)
        print(
            f"Front Desk: created new Desktop Icon record "
            f"(name={new_doc.name!r}) with logo_url={CORRECT_LOGO_URL!r}"
        )

    frappe.db.commit()

    print()
    print("=== Verification ===")
    for name in ["Impact Health Studio", "Front Desk"]:
        if frappe.db.exists("Desktop Icon", name):
            logo_url = frappe.db.get_value("Desktop Icon", name, "logo_url")
            print(f"  {name}: logo_url={logo_url!r}")
        else:
            print(f"  {name}: still does not exist")
