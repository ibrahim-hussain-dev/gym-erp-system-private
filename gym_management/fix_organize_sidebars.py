import frappe


def _item(label, link_type, link_to, type_="Link", icon="list", child=0, collapsible=1, indent=0):
    return {
        "label": label,
        "link_type": link_type,
        "link_to": link_to,
        "type": type_,
        "icon": icon,
        "child": child,
        "collapsible": collapsible,
        "indent": indent,
        "keep_closed": 0,
        "show_arrow": 0,
        "url": None,
        "filters": None,
        "route_options": None,
        "navigate_to_tab": None,
    }


def _set_sidebar(sidebar_name, items):
    if frappe.db.exists("Workspace Sidebar", sidebar_name):
        doc = frappe.get_doc("Workspace Sidebar", sidebar_name)
        doc.items = []
        for it in items:
            doc.append("items", it)
        doc.save(ignore_permissions=True)
        print(f"  Updated existing Workspace Sidebar '{sidebar_name}'")
    else:
        doc = frappe.new_doc("Workspace Sidebar")
        doc.title = sidebar_name
        doc.module = "Gym-ERP-System"
        doc.standard = 1
        doc.app = "gym_management"
        for it in items:
            doc.append("items", it)
        doc.insert(ignore_permissions=True)
        print(f"  Created new Workspace Sidebar '{sidebar_name}'")
    return doc


def run():
    print("=" * 80)
    print("STEP 1: reorganize 'Impact Health Studio' Workspace Sidebar into clear sections")
    print("=" * 80)
    owner_items = [
        _item("Impact Health Studio", "Workspace", "Impact Health Studio"),

        _item("Quick Access", None, None, type_="Section Break"),
        _item("Sell Membership", "Page", "sell-membership"),
        _item("Gym Members", "DocType", "Gym Member"),
        _item("Attendance Log", "DocType", "Gym Attendance"),
        _item("Gym Subscription", "DocType", "Gym Subscription"),

        _item("Setup", None, None, type_="Section Break"),
        _item("Gym Plan", "DocType", "Gym Plan"),
        _item("Membership Plan", "DocType", "Gym Plan"),
        _item("Promo Codes", "DocType", "Gym Promo Code"),
        _item("Gym Trainer", "DocType", "Gym Trainer"),
        _item("Gym Timing Slot", "DocType", "Gym Timing Slot"),

        _item("Billing", None, None, type_="Section Break"),
        _item("Payment Entry", "DocType", "Payment Entry"),
        _item("Gym Invoices", "DocType", "Sales Invoice"),
        _item("Gym Expense", "DocType", "Gym Expense"),
        _item("Record Expense", "Page", "record-expense"),

        _item("Fitness", None, None, type_="Section Break"),
        _item("Gym Fitness Log", "DocType", "Gym Fitness Log"),
        _item("Mark Attendance", "Page", "mark-attendance"),

        _item("Reports", None, None, type_="Section Break"),
        _item("Gym Trainer Commission", "Report", "Gym Trainer Commission"),
        _item("Revenue by Plan", "Report", "Gym Revenue by Plan"),
        _item("Gym Revenue", "Report", "Gym Monthly Revenue"),
        _item("Member Retention", "Report", "Gym Member Retention", icon="table"),
    ]
    _set_sidebar("Impact Health Studio", owner_items)

    print()
    print("=" * 80)
    print("STEP 2: create/organize 'Front Desk' Workspace Sidebar (adds Gym Trainer + Record Expense access nav)")
    print("=" * 80)
    fd_items = [
        _item("Front Desk", "Workspace", "Front Desk"),

        _item("Quick Access", None, None, type_="Section Break"),
        _item("Sell Membership", "Page", "sell-membership"),
        _item("Gym Member", "DocType", "Gym Member"),
        _item("Mark Attendance", "Page", "mark-attendance"),
        _item("Attendance Log", "DocType", "Gym Attendance"),

        _item("Members", None, None, type_="Section Break"),
        _item("Gym Subscription", "DocType", "Gym Subscription"),
        _item("Gym Trainer", "DocType", "Gym Trainer"),

        _item("Billing", None, None, type_="Section Break"),
        _item("Gym Invoices", "DocType", "Sales Invoice"),
        _item("Record Expense", "Page", "record-expense"),

        _item("Fitness", None, None, type_="Section Break"),
        _item("Gym Fitness Log", "DocType", "Gym Fitness Log"),
    ]
    _set_sidebar("Front Desk", fd_items)

    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("VERIFICATION - Impact Health Studio items:")
    d1 = frappe.get_doc("Workspace Sidebar", "Impact Health Studio")
    for it in d1.items:
        print(f"  idx={it.idx} label={it.label!r} type={it.type} link_type={it.link_type} link_to={it.link_to}")

    print()
    print("VERIFICATION - Front Desk items:")
    d2 = frappe.get_doc("Workspace Sidebar", "Front Desk")
    for it in d2.items:
        print(f"  idx={it.idx} label={it.label!r} type={it.type} link_type={it.link_type} link_to={it.link_to}")

    print()
    print("DONE.")
