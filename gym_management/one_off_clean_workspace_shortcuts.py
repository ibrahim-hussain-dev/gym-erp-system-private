import frappe

def run():
    doc = frappe.get_doc("Workspace", "Gym Operations")

    dead_links = {"manage-subscription", "Gym Membership Retention"}

    before = len(doc.shortcuts)
    kept = []
    removed = []
    for row in doc.shortcuts:
        if row.link_to in dead_links:
            removed.append(f"Row #{row.idx}: {row.link_to}")
        else:
            kept.append(row)

    doc.shortcuts = []
    for row in kept:
        doc.append("shortcuts", row)

    doc.flags.ignore_links = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    print(f"Before: {before} shortcuts, After: {len(doc.shortcuts)} shortcuts")
    print("Removed:", removed)
