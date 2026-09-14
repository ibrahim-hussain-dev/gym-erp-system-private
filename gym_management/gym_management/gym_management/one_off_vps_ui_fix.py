import frappe

def run():
    # 1. Create the Workspace Sidebar record (Gym Operations)
    if not frappe.db.exists("Workspace Sidebar", "Gym Operations"):
        frappe.get_doc({
            "doctype": "Workspace Sidebar",
            "name": "Gym Operations",
            "header_icon": "dumbbell",
            "module": "Gym-ERP-System",
            "standard": 1,
            "title": "Gym Operations",
            "items": [
                {"label": "Gym Operations", "link_to": "Gym Operations", "link_type": "Workspace", "type": "Link", "icon": "list"},
                {"label": "Sell Membership", "link_to": "sell-membership", "link_type": "Page", "type": "Link", "icon": "list"},
                {"label": "Gym Members", "link_to": "Gym Member", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Mark Attendance", "link_to": "mark-attendance", "link_type": "Page", "type": "Link", "icon": "list"},
                {"label": "Attendance Log", "link_to": "Gym Attendance", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Gym Plan", "link_to": "Gym Plan", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Membership Plan", "link_to": "Gym Plan", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Promo Codes", "link_to": "Gym Promo Code", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Gym Trainer", "link_to": "Gym Trainer", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Gym Timing Slot", "link_to": "Gym Timing Slot", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Gym Fitness Log", "link_to": "Gym Fitness Log", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Gym Subscription", "link_to": "Gym Subscription", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Payment Entry", "link_to": "Payment Entry", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Record Expense", "link_to": "record-expense", "link_type": "Page", "type": "Link", "icon": "list"},
                {"label": "Gym Expense", "link_to": "Gym Expense", "link_type": "DocType", "type": "Link", "icon": "list"},
                {"label": "Reports", "link_type": "DocType", "type": "Section Break", "icon": "list"},
                {"label": "Gym Trainer Commission", "link_to": "Gym Trainer Commission", "link_type": "Report", "type": "Link", "icon": "list"},
                {"label": "Revenue by Plan", "link_to": "Gym Revenue by Plan", "link_type": "Report", "type": "Link", "icon": "list"},
                {"label": "Gym Revenue", "link_to": "Gym Monthly Revenue", "link_type": "Report", "type": "Link", "icon": "list"},
                {"label": "Member Retention", "link_to": "Gym Member Retention", "link_type": "Report", "type": "Link", "icon": "table"},
            ],
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Workspace Sidebar: Gym Operations")
    else:
        print("Workspace Sidebar 'Gym Operations' already exists")

    # 2. Fix roles for the test user - remove generic ERPNext roles, add Gym Manager
    user_email = "iibrahimhere@gmail.com"
    if frappe.db.exists("User", user_email):
        user = frappe.get_doc("User", user_email)
        keep_roles = {"System Manager", "Gym Manager", "Gym Front Desk", "Gym Trainer", "All"}
        removed = []
        for r in list(user.roles):
            if r.role not in keep_roles:
                removed.append(r.role)
        user.roles = [r for r in user.roles if r.role in keep_roles]
        if not any(r.role == "Gym Manager" for r in user.roles):
            user.append("roles", {"role": "Gym Manager"})
        user.save(ignore_permissions=True)
        frappe.db.commit()
        print("Removed generic roles:", removed)
        print("User now has roles:", [r.role for r in user.roles])
    else:
        print("WARNING: user", user_email, "not found")

    print("DONE")
