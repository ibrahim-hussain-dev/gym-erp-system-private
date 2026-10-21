import frappe


def run():
    print("=" * 80)
    print("Adding 'Gym Invoices' (-> Sales Invoice) to Workspace Sidebar 'Impact Health Studio'")
    print("=" * 80)

    doc = frappe.get_doc("Workspace Sidebar", "Impact Health Studio")

    already = [it for it in doc.items if it.link_to == "Sales Invoice" and it.link_type == "DocType"]
    if already:
        print("  Already present, nothing to do:", already[0].as_dict())
        print("DONE.")
        return

    payment_entry_idx = None
    for it in doc.items:
        if it.link_to == "Payment Entry" and it.link_type == "DocType":
            payment_entry_idx = it.idx
            break

    if payment_entry_idx is None:
        print("  WARNING: could not find 'Payment Entry' row to anchor on, appending at end instead")
        doc.append("items", {
            "label": "Gym Invoices",
            "link_type": "DocType",
            "link_to": "Sales Invoice",
            "icon": "list",
            "type": "Link",
            "child": 0,
            "collapsible": 1,
        })
    else:
        # shift idx of every row that comes after Payment Entry, then insert the new row
        # right after it, then renumber everything cleanly at the end.
        new_row = {
            "label": "Gym Invoices",
            "link_type": "DocType",
            "link_to": "Sales Invoice",
            "icon": "list",
            "type": "Link",
            "child": 0,
            "collapsible": 1,
        }
        rows_as_dicts = [it.as_dict() for it in doc.items]
        insert_at = None
        for i, r in enumerate(rows_as_dicts):
            if r.get("link_to") == "Payment Entry" and r.get("link_type") == "DocType":
                insert_at = i + 1
                break
        rows_as_dicts.insert(insert_at, new_row)

        doc.items = []
        for r in rows_as_dicts:
            doc.append("items", {
                "label": r.get("label"),
                "link_type": r.get("link_type"),
                "link_to": r.get("link_to"),
                "icon": r.get("icon"),
                "type": r.get("type"),
                "child": r.get("child") or 0,
                "collapsible": r.get("collapsible") if r.get("collapsible") is not None else 1,
                "indent": r.get("indent") or 0,
                "keep_closed": r.get("keep_closed") or 0,
                "show_arrow": r.get("show_arrow") or 0,
                "url": r.get("url"),
                "filters": r.get("filters"),
                "route_options": r.get("route_options"),
                "navigate_to_tab": r.get("navigate_to_tab"),
            })

    doc.save(ignore_permissions=True)
    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("VERIFICATION - full items list after save:")
    doc2 = frappe.get_doc("Workspace Sidebar", "Impact Health Studio")
    for it in doc2.items:
        print(f"  idx={it.idx} label={it.label!r} type={it.type} link_type={it.link_type} link_to={it.link_to}")

    print()
    print("DONE.")
