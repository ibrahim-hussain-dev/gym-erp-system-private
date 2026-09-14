import frappe
import json

BENCH = "/home/frappe/frappe-bench/"
REPORT_PATH = BENCH + "apps/gym_management/gym_management/gym_erp_system/report/gym_cash_collection_report/gym_cash_collection_report.py"


def run():
    print("=" * 70)
    print("STEP 0: actual Company records + sample company values on SI/PE")
    print("=" * 70)
    companies = frappe.get_all("Company", fields=["name", "abbr"])
    print("Company records:", companies)

    si_companies = frappe.db.sql("select distinct company, count(*) as c from `tabSales Invoice` group by company", as_dict=True)
    print("Distinct Sales Invoice.company values:", si_companies)

    pe_companies = frappe.db.sql("select distinct company, count(*) as c from `tabPayment Entry` group by company", as_dict=True)
    print("Distinct Payment Entry.company values:", pe_companies)

    if len(companies) != 1:
        print("STOPPING: expected exactly 1 Company record, found", len(companies), "- not auto-fixing, please tell me which company to use.")
        return

    company = companies[0].name
    print(f"Using company = {company!r} for the fix.")

    print("=" * 70)
    print("STEP 1: fix 'Total Outstanding Receivables' Number Card")
    print("=" * 70)
    if frappe.db.exists("Number Card", "Total Outstanding Receivables"):
        card = frappe.get_doc("Number Card", "Total Outstanding Receivables")
        new_filters = [
            ["Sales Invoice", "docstatus", "=", 1],
            ["Sales Invoice", "outstanding_amount", ">", 0],
            ["Sales Invoice", "company", "=", company],
        ]
        card.filters_json = json.dumps(new_filters)
        card.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated filters_json:", card.filters_json)
    else:
        print("Number Card 'Total Outstanding Receivables' not found!")

    print("=" * 70)
    print("STEP 2: fix 'Today's Cash Collected' Number Card")
    print("=" * 70)
    if frappe.db.exists("Number Card", "Today's Cash Collected"):
        card = frappe.get_doc("Number Card", "Today's Cash Collected")
        new_filters = [
            ["Payment Entry", "docstatus", "=", 1],
            ["Payment Entry", "payment_type", "=", "Receive"],
            ["Payment Entry", "company", "=", company],
            ["Payment Entry", "posting_date", "Timespan", "today"],
        ]
        card.filters_json = json.dumps(new_filters)
        card.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated filters_json:", card.filters_json)
    else:
        print("Number Card \"Today's Cash Collected\" not found!")

    print("=" * 70)
    print("STEP 3: patch hardcoded 'Gym ERP' company in Gym Cash Collection Report")
    print("=" * 70)
    with open(REPORT_PATH) as f:
        content = f.read()
    occurrences = content.count('"Gym ERP"')
    print(f"Found {occurrences} occurrence(s) of literal \"Gym ERP\" in the report file.")
    if occurrences:
        content = content.replace('"Gym ERP"', f'"{company}"')
        with open(REPORT_PATH, "w") as f:
            f.write(content)
        print(f"Replaced all occurrences with {company!r}.")
    else:
        print("Nothing to replace.")

    frappe.clear_cache()

    print("=" * 70)
    print("STEP 4: verify - run the same aggregate queries the cards use")
    print("=" * 70)
    outstanding = frappe.db.sql(
        "select sum(outstanding_amount) from `tabSales Invoice` where docstatus=1 and outstanding_amount>0 and company=%s",
        (company,),
    )[0][0]
    print("Total Outstanding Receivables (recomputed):", outstanding)

    today_cash = frappe.db.sql(
        "select sum(paid_amount) from `tabPayment Entry` where docstatus=1 and payment_type='Receive' and company=%s and posting_date=CURDATE()",
        (company,),
    )[0][0]
    print("Today's Cash Collected (recomputed):", today_cash)

    print("DONE.")
