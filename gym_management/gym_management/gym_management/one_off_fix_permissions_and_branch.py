import frappe


def ensure_item_price_perm(role):
    existing = frappe.db.exists("Custom DocPerm", {"parent": "Item Price", "role": role, "permlevel": 0})
    if existing:
        doc = frappe.get_doc("Custom DocPerm", existing)
        changed = False
        for f in ("read", "write", "create"):
            if not doc.get(f):
                doc.set(f, 1)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
        print(f"Item Price perm already existed for {role}, ensured read/write/create=1")
        return
    doc = frappe.new_doc("Custom DocPerm")
    doc.parent = "Item Price"
    doc.parenttype = "DocType"
    doc.parentfield = "permissions"
    doc.role = role
    doc.permlevel = 0
    doc.read = 1
    doc.write = 1
    doc.create = 1
    doc.delete = 0
    doc.insert(ignore_permissions=True)
    print(f"Created Item Price Custom DocPerm for role: {role}")


def run():
    # 1. Item Price permission for Gym Owner + Temporary Developer
    for role in ("Gym Owner", "Temporary Developer"):
        ensure_item_price_perm(role)
    frappe.db.commit()

    # 2. Add 'branch' Link field to Gym Member
    original_dev_mode = frappe.conf.developer_mode
    frappe.conf.developer_mode = 1
    try:
        dt = frappe.get_doc("DocType", "Gym Member")
        if any(f.fieldname == "branch" for f in dt.fields):
            print("Gym Member already has 'branch' field, skipping.")
        else:
            idx = next((i for i, f in enumerate(dt.fields) if f.fieldname == "membership_status"), len(dt.fields) - 1)
            new_field = dt.append("fields", {})
            new_field.fieldname = "branch"
            new_field.fieldtype = "Link"
            new_field.options = "Gym Branch"
            new_field.label = "Branch"
            new_field.reqd = 0
            dt.fields.remove(new_field)
            dt.fields.insert(idx + 1, new_field)
            for i, f in enumerate(dt.fields):
                f.idx = i + 1
            dt.save(ignore_permissions=True)
            frappe.db.commit()
            print("Added 'branch' (Link -> Gym Branch) field to Gym Member DocType.")
    finally:
        frappe.conf.developer_mode = original_dev_mode

    frappe.clear_cache()
    print("DONE")
