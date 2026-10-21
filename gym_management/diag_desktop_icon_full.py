import frappe


def run():
    print("=== Desktop Icon: Impact Health Studio (full doc) ===")
    if frappe.db.exists("Desktop Icon", "Impact Health Studio"):
        doc = frappe.get_doc("Desktop Icon", "Impact Health Studio")
        for key, value in doc.as_dict().items():
            if key in ("creation", "modified", "owner", "modified_by", "docstatus", "idx"):
                continue
            print(f"  {key}: {value!r}")
    else:
        print("  DOES NOT EXIST")

    print()
    print("=== Desktop Icon: Front Desk (full doc) ===")
    if frappe.db.exists("Desktop Icon", "Front Desk"):
        doc = frappe.get_doc("Desktop Icon", "Front Desk")
        for key, value in doc.as_dict().items():
            if key in ("creation", "modified", "owner", "modified_by", "docstatus", "idx"):
                continue
            print(f"  {key}: {value!r}")
    else:
        print("  DOES NOT EXIST")

    print()
    print("=== All Desktop Icon records (name, label, module, logo_url) ===")
    rows = frappe.get_all(
        "Desktop Icon",
        fields=["name", "label", "module", "logo_url", "icon", "standard"],
    )
    for r in rows:
        print(f"  {r}")
