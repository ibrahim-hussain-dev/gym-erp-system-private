import frappe
import os
import shutil
import json

BENCH = "/home/frappe/frappe-bench/"
APP_ROOT = BENCH + "apps/gym_management/"
PKG = APP_ROOT + "gym_management/"


def ensure_custom_field(dt, fieldname, **kwargs):
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
        print(f"Custom Field {dt}.{fieldname} already exists, skipping.")
        return
    meta = frappe.get_meta(dt)
    if meta.has_field(fieldname):
        print(f"{dt}.{fieldname} already exists as a native field, skipping.")
        return
    cf = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": fieldname,
        **kwargs,
    })
    cf.insert(ignore_permissions=True)
    print(f"Created Custom Field {dt}.{fieldname}")


def run():
    print("=" * 70)
    print("STEP 0: DIAGNOSTICS (read-only)")
    print("=" * 70)

    print("developer_mode (site_config):", frappe.conf.get("developer_mode"))

    pages_by_name = frappe.get_all("Page", filters=[["name", "like", "%pt%session%"]], fields=["name", "title", "module"])
    pages_by_title = frappe.get_all("Page", filters=[["title", "like", "%PT Session%"]], fields=["name", "title", "module"])
    pt_pages = list({p.name: p for p in (pages_by_name + pages_by_title)}.values())
    print("Candidate 'Book PT Session' Page records:", pt_pages)

    print("Gym Slot DocType exists:", frappe.db.exists("DocType", "Gym Slot"))

    hooks_path = PKG + "hooks.py"
    with open(hooks_path) as f:
        hooks_content = f.read()
    print("--- hooks.py lines mentioning branch/sessions_attended/total_commission/plan_price ---")
    for i, line in enumerate(hooks_content.splitlines(), 1):
        if any(tok in line for tok in ["branch", "sessions_attended", "total_commission", "plan_price"]):
            print(f"{i}: {line}")

    js_path = PKG + "gym_erp_system/page/sell_membership/sell_membership.js"
    with open(js_path) as f:
        js_content = f.read()
    idx = js_content.find("promo_code")
    if idx != -1:
        print("--- sell_membership.js context around first 'promo_code' occurrence ---")
        print(js_content[max(0, idx - 200):idx + 400])
    else:
        print("'promo_code' string not found anywhere in sell_membership.js")

    print("=" * 70)
    print("STEP 1: FINISH PT-BOOKING REMOVAL (Page + DocType), properly guarded")
    print("=" * 70)

    original_dev_mode = frappe.conf.get("developer_mode")
    frappe.conf.developer_mode = 1
    try:
        for p in pt_pages:
            try:
                frappe.delete_doc("Page", p.name, ignore_permissions=True, force=True)
                print(f"Deleted Page: {p.name}")
            except Exception:
                print(f"FAILED to delete Page {p.name}:")
                print(frappe.get_traceback())

        if frappe.db.exists("DocType", "Gym Slot"):
            try:
                frappe.delete_doc("DocType", "Gym Slot", ignore_permissions=True, force=True)
                print("Deleted DocType: Gym Slot")
            except Exception:
                print("FAILED to delete DocType Gym Slot:")
                print(frappe.get_traceback())
        else:
            print("DocType Gym Slot already gone, skipping.")

        frappe.db.commit()
    finally:
        frappe.conf.developer_mode = original_dev_mode

    for t in [PKG + "gym_erp_system/doctype/gym_slot", PKG + "gym_erp_system/page/book_pt_session"]:
        if os.path.isdir(t):
            shutil.rmtree(t)
            print(f"Removed folder: {t}")
        else:
            print(f"Folder not present (already removed?): {t}")

    slot_module = PKG + "gym_erp_system/gym_slot.py"
    if os.path.isfile(slot_module):
        os.remove(slot_module)
        print(f"Removed module: {slot_module}")
    else:
        print(f"Module not present (already removed?): {slot_module}")

    print("=" * 70)
    print("STEP 1b: WORKSPACE SHORTCUT CLEANUP (residual PT/Slot entries)")
    print("=" * 70)
    ws_name = "Impact Health Studio"
    if frappe.db.exists("Workspace", ws_name):
        ws = frappe.get_doc("Workspace", ws_name)
        bad_labels = ["book pt session", "gym slot", "book pt slot"]

        def is_bad(label):
            if not label:
                return False
            l = label.strip().lower()
            return any(b in l for b in bad_labels)

        before = len(ws.shortcuts)
        ws.shortcuts = [s for s in ws.shortcuts if not is_bad(s.label or s.link_to)]
        after = len(ws.shortcuts)

        try:
            content = json.loads(ws.content or "[]")
        except Exception:
            content = []
        new_content = []
        removed_blocks = 0
        for block in content:
            if block.get("type") == "shortcut":
                sc_name = (block.get("data") or {}).get("shortcut_name", "")
                if is_bad(sc_name):
                    removed_blocks += 1
                    continue
            new_content.append(block)
        ws.content = json.dumps(new_content)

        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Workspace '{ws_name}': shortcuts {before} -> {after}, removed {removed_blocks} content block(s)")
    else:
        print(f"Workspace '{ws_name}' not found, skipping shortcut cleanup.")

    print("=" * 70)
    print("STEP 2: NEW COMMISSION SYSTEM FIELDS")
    print("=" * 70)

    ensure_custom_field(
        "Gym Plan", "trainer",
        fieldtype="Link", options="Gym Trainer", label="Trainer",
        insert_after="plan_group",
        description="For Personal Training plans: the trainer this plan's commission is credited to on sale.",
    )

    ensure_custom_field(
        "Gym Trainer", "commission_percentage",
        fieldtype="Percent", label="Commission %",
        insert_after="trainer_name",
        description="Percentage of each PT plan's sale amount credited to this trainer on sale.",
    )

    ensure_custom_field(
        "Gym Trainer", "total_commission_earned",
        fieldtype="Currency", label="Total Commission Earned",
        insert_after="commission_percentage",
        default="0", read_only=1,
        description="Running total of commission earned from all PT plan sales credited to this trainer.",
    )

    print("=" * 70)
    print("STEP 3: 'Gym Trainer Commission' log DocType")
    print("=" * 70)

    if frappe.db.exists("DocType", "Gym Trainer Commission"):
        print("DocType 'Gym Trainer Commission' already exists, skipping.")
    else:
        module = frappe.db.get_value("DocType", "Gym Member", "module")
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Gym Trainer Commission",
            "module": module,
            "custom": 0,
            "naming_rule": "Random",
            "autoname": "hash",
            "fields": [
                {"fieldname": "trainer", "fieldtype": "Link", "options": "Gym Trainer", "label": "Trainer", "reqd": 1, "in_list_view": 1},
                {"fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "label": "Sales Invoice", "reqd": 1, "in_list_view": 1},
                {"fieldname": "member", "fieldtype": "Link", "options": "Gym Member", "label": "Member", "in_list_view": 1},
                {"fieldname": "gym_plan", "fieldtype": "Link", "options": "Gym Plan", "label": "Gym Plan", "in_list_view": 1},
                {"fieldname": "sale_amount", "fieldtype": "Currency", "label": "Sale Amount"},
                {"fieldname": "commission_percentage", "fieldtype": "Percent", "label": "Commission %"},
                {"fieldname": "commission_amount", "fieldtype": "Currency", "label": "Commission Amount", "in_list_view": 1},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "in_list_view": 1},
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
                {"role": "Gym Owner", "read": 1, "report": 1, "export": 1, "print": 1},
            ],
            "sort_field": "creation",
            "sort_order": "DESC",
        })
        original_dev_mode2 = frappe.conf.get("developer_mode")
        frappe.conf.developer_mode = 1
        try:
            doc.insert(ignore_permissions=True)
            print("Created DocType: Gym Trainer Commission")
        finally:
            frappe.conf.developer_mode = original_dev_mode2

    frappe.clear_cache(doctype="Gym Trainer Commission")
    frappe.db.commit()

    print("=" * 70)
    print("STEP 4: FINAL SANITY CHECKS")
    print("=" * 70)
    print("Gym Plan has 'trainer' field:", frappe.get_meta("Gym Plan").has_field("trainer"))
    print("Gym Trainer has 'commission_percentage' field:", frappe.get_meta("Gym Trainer").has_field("commission_percentage"))
    print("Gym Trainer has 'total_commission_earned' field:", frappe.get_meta("Gym Trainer").has_field("total_commission_earned"))
    print("Gym Trainer Commission doctype exists:", frappe.db.exists("DocType", "Gym Trainer Commission"))
    print("Gym Slot doctype exists (should be False now):", frappe.db.exists("DocType", "Gym Slot"))
    print("ALL DONE.")
