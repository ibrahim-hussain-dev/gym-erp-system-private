import frappe

def run():
    doc = frappe.get_doc("Workspace", "Gym Operations")
    dead_links = {"manage-subscription", "Gym Membership Retention"}

    meta = frappe.get_meta("Workspace")
    child_table_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Table"]
    print("Child tables on Workspace:", child_table_fields)

    for fieldname in child_table_fields:
        rows = doc.get(fieldname) or []
        if not rows or not hasattr(rows[0], "link_to"):
            continue
        before = len(rows)
        removed = [r.link_to for r in rows if r.link_to in dead_links]
        kept = [r for r in rows if r.link_to not in dead_links]
        doc.set(fieldname, [])
        for r in kept:
            doc.append(fieldname, r)
        print(f"{fieldname}: before={before} after={len(kept)} removed={removed}")

    doc.flags.ignore_links = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Saved successfully.")
