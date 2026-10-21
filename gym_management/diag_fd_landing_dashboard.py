import json

import frappe


def run():
    print("=" * 80)
    print("STEP 1: default_workspace for fd1@gym.local and owner@gym.local")
    print("=" * 80)
    for u in ["fd1@gym.local", "owner@gym.local"]:
        if frappe.db.exists("User", u):
            dv = frappe.db.get_value("User", u, "default_workspace")
            roles = frappe.get_roles(u)
            print(f"  {u}: default_workspace={dv}, roles={roles}")

    print()
    print("=" * 80)
    print("STEP 2: does gym_management have a one_off_set_default_workspace.py helper already?")
    print("=" * 80)
    import os
    path = "/home/frappe/frappe-bench/apps/gym_management/gym_management/one_off_set_default_workspace.py"
    if os.path.exists(path):
        with open(path) as f:
            print(f.read())
    else:
        print("  not found")

    print()
    print("=" * 80)
    print("STEP 3: 'content' (number_card / stat tiles) for Front Desk and Impact Health Studio workspaces")
    print("=" * 80)
    for ws in ["Front Desk", "Impact Health Studio"]:
        if frappe.db.exists("Workspace", ws):
            doc = frappe.get_doc("Workspace", ws)
            print(f"--- {ws} ---")
            try:
                content = json.loads(doc.content) if doc.content else []
                print(json.dumps(content, indent=2))
            except Exception as e:
                print("  could not parse content:", e)
            print()

    print("=" * 80)
    print("STEP 4: existing 'Number Card' doctype records (module Gym-ERP-System)")
    print("=" * 80)
    cards = frappe.get_all(
        "Number Card",
        filters={"module": "Gym-ERP-System"},
        fields=["name", "label", "document_type", "function", "aggregate_function_based_on", "filters_json"],
    )
    for c in cards:
        print("  ", c)

    print()
    print("=" * 80)
    print("STEP 5: Website Settings full image-related fields (favicon, app_logo, banner)")
    print("=" * 80)
    ws_doc = frappe.get_single("Website Settings")
    for f in ["app_logo", "favicon", "banner_image", "splash_image"]:
        if hasattr(ws_doc, f):
            print(f"  Website Settings.{f} = {getattr(ws_doc, f)}")
    fav = getattr(ws_doc, "favicon", None)
    if fav:
        frec = frappe.db.get_value("File", {"file_url": fav}, ["name", "is_private", "file_url"], as_dict=True)
        print(f"  File record for favicon {fav}: {frec}")

    print()
    print("DONE.")
