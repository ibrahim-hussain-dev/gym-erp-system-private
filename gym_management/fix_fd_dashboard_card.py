import json

import frappe


def run():
    print("=" * 80)
    print("STEP 1: create 'Total Members' Number Card (cloned from 'Today's Check-ins' to inherit all required fields safely)")
    print("=" * 80)

    if frappe.db.exists("Number Card", "Total Members"):
        print("  'Total Members' Number Card already exists, skipping creation")
        card_name = "Total Members"
    else:
        source = frappe.get_doc("Number Card", "Today's Check-ins")
        new_card = frappe.copy_doc(source)
        new_card.label = "Total Members"
        new_card.document_type = "Gym Member"
        new_card.function = "Count"
        new_card.aggregate_function_based_on = None
        new_card.filters_json = "[]"
        new_card.insert(ignore_permissions=True)
        card_name = new_card.name
        print(f"  Created Number Card '{card_name}'")

    print()
    print("=" * 80)
    print("STEP 2: add this card as a 3rd stat tile on the 'Front Desk' workspace dashboard")
    print("=" * 80)
    ws = frappe.get_doc("Workspace", "Front Desk")
    content = json.loads(ws.content) if ws.content else []

    already = [b for b in content if b.get("type") == "number_card" and b.get("data", {}).get("number_card_name") == card_name]
    if already:
        print("  Already present on Front Desk dashboard, nothing to do")
    else:
        # insert right after the existing "Active Memberships" number_card block (id fnc2)
        insert_at = None
        for i, b in enumerate(content):
            if b.get("id") == "fnc2":
                insert_at = i + 1
                break
        new_block = {
            "id": "fnc3",
            "type": "number_card",
            "data": {"number_card_name": card_name, "col": 4},
        }
        if insert_at is None:
            content.append(new_block)
        else:
            content.insert(insert_at, new_block)
        ws.content = json.dumps(content)
        ws.save(ignore_permissions=True)
        print("  Added 'Total Members' tile to Front Desk dashboard")

    frappe.clear_cache()
    frappe.db.commit()

    print()
    print("VERIFICATION - Front Desk content blocks:")
    ws2 = frappe.get_doc("Workspace", "Front Desk")
    for b in json.loads(ws2.content):
        print("  ", b.get("id"), b.get("type"), b.get("data"))

    print()
    print("DONE.")
