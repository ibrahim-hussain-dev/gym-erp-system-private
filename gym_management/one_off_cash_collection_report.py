import frappe

def run():
    # Script Report
    if not frappe.db.exists("Report", "Gym Cash Collection Report"):
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": "Gym Cash Collection Report",
            "report_type": "Script Report",
            "module": "Gym-ERP-System",
            "ref_doctype": "Sales Invoice",
            "is_standard": "Yes",
        })
        report.append("roles", {"role": "Gym Manager"})
        report.append("roles", {"role": "Gym Front Desk"})
        report.insert(ignore_permissions=True)
        print("Created Report: Gym Cash Collection Report")
    else:
        print("Report already exists, skipping")

    # Number Card 1: Total Outstanding Receivables (reliable, no date dependency)
    if not frappe.db.exists("Number Card", "Total Outstanding Receivables"):
        frappe.get_doc({
            "doctype": "Number Card",
            "label": "Total Outstanding Receivables",
            "document_type": "Sales Invoice",
            "function": "Sum",
            "aggregate_function_based_on": "outstanding_amount",
            "filters_json": frappe.as_json([
                ["Sales Invoice", "docstatus", "=", 1],
                ["Sales Invoice", "outstanding_amount", ">", 0],
                ["Sales Invoice", "company", "=", "Gym ERP"],
            ]),
            "is_public": 1,
            "show_percentage_stats": 0,
        }).insert(ignore_permissions=True)
        print("Created Number Card: Total Outstanding Receivables")
    else:
        print("Number Card 'Total Outstanding Receivables' already exists, skipping")

    # Number Card 2: Today's Cash Collected (best-effort, please verify visually)
    if not frappe.db.exists("Number Card", "Today's Cash Collected"):
        frappe.get_doc({
            "doctype": "Number Card",
            "label": "Today's Cash Collected",
            "document_type": "Payment Entry",
            "function": "Sum",
            "aggregate_function_based_on": "paid_amount",
            "filters_json": frappe.as_json([
                ["Payment Entry", "docstatus", "=", 1],
                ["Payment Entry", "payment_type", "=", "Receive"],
                ["Payment Entry", "company", "=", "Gym ERP"],
                ["Payment Entry", "posting_date", "=", "Today"],
            ]),
            "is_public": 1,
            "show_percentage_stats": 0,
        }).insert(ignore_permissions=True)
        print("Created Number Card: Today's Cash Collected (VERIFY the number manually - see Step 4)")
    else:
        print("Number Card 'Today's Cash Collected' already exists, skipping")

    print("Done")
