import frappe

# The console evidence you just sent shows the real internal Frappe routes
# are NOT the hyphenated URL slugs I assumed -- e.g. /desk/gym-member
# resolves internally to ["List", "Gym Member", "List"], and /desk/front-desk
# resolves to ["Workspaces", "Front Desk"]. This script verifies, from the
# database directly (no guessing), the exact DocType/Page/Workspace names
# behind every slug in both allowed-page lists, plus checks for the
# duplicate "Impact Health Studio" workspace you noticed.

SLUGS = {
    "gym-member": "Gym Member",
    "gym-attendance": "Gym Attendance",
    "gym-subscription": "Gym Subscription",
    "gym-trainer": "Gym Trainer",
    "sales-invoice": "Sales Invoice",
    "gym-fitness-log": "Gym Fitness Log",
    "gym-plan": "Gym Plan",
    "gym-timing-slot": "Gym Timing Slot",
    "payment-entry": "Payment Entry",
    "gym-expense": "Gym Expense",
}


def slugify(name):
    return name.lower().replace(" ", "-")


def run():
    print("=== DocType existence + slug check (List view route = ['List', <this name>, 'List']) ===")
    for slug, guessed_name in SLUGS.items():
        exists = frappe.db.exists("DocType", guessed_name)
        matches = slugify(guessed_name) == slug
        print(
            f"  slug={slug!r} guessed_doctype={guessed_name!r} "
            f"exists_in_db={bool(exists)} slug_matches={matches}"
        )

    print()
    print("=== Page doctype check (Page route = [<page-name>], single segment) ===")
    for page_name in ["record-expense", "mark-attendance", "sell-membership", "front-desk", "impact-health-studio"]:
        exists = frappe.db.exists("Page", page_name)
        print(f"  Page name={page_name!r} exists_as_Page={bool(exists)}")
        if exists:
            title = frappe.db.get_value("Page", page_name, "title")
            print(f"    title={title!r}")

    print()
    print("=== Workspace records matching 'Front Desk' or 'Impact' (checking for duplicates) ===")
    rows = frappe.db.sql(
        """select name, title, parent_page, module, public, is_hidden
           from `tabWorkspace`
           where title like %s or title like %s or name like %s or name like %s""",
        ("%Front Desk%", "%Impact%", "%Front Desk%", "%Impact%"),
        as_dict=True,
    )
    for r in rows:
        print(f"  {r}")

    print()
    print("=== Report records for the 4 Owner query-report links (exact name match) ===")
    for report_name in [
        "Gym Trainer Commission",
        "Gym Revenue by Plan",
        "Gym Monthly Revenue",
        "Gym Member Retention",
    ]:
        exists = frappe.db.exists("Report", report_name)
        print(f"  Report name={report_name!r} exists={bool(exists)}")

    print()
    print("=== All DocTypes starting with 'Gym' (sanity check exact spelling/casing) ===")
    rows = frappe.get_all("DocType", filters={"name": ["like", "Gym%"]}, fields=["name"], order_by="name")
    for r in rows:
        print(f"  {r['name']}")
