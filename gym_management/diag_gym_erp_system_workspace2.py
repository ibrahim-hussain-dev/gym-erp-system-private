import frappe


def run():
    print("=" * 80)
    print("full Workspace listing + app_title check")
    print("=" * 80)

    print("--- ALL Workspace docs (name / module / label / public / is_hidden) ---")
    for w in frappe.get_all(
        "Workspace",
        fields=["name", "module", "label", "public", "is_hidden"],
        order_by="name",
    ):
        print(f"  name={w.name!r:30} module={w.module!r:25} label={w.label!r:25} public={w.public} is_hidden={w.is_hidden}")

    print()
    print("--- Workspace docs where name or label mentions 'Gym' or 'ERP' ---")
    for w in frappe.get_all(
        "Workspace",
        fields=["name", "module", "label", "public", "is_hidden"],
    ):
        blob = f"{w.name} {w.label}".lower()
        if "gym" in blob or "erp" in blob:
            print(f"  name={w.name!r:30} module={w.module!r:25} label={w.label!r:25} public={w.public} is_hidden={w.is_hidden}")

    print()
    print("--- gym_management app_title / hooks ---")
    import gym_management.hooks as h
    print("  app_title:", getattr(h, "app_title", None))
    print("  app_name:", getattr(h, "app_name", None))

    print()
    print("--- modules.txt for gym_management ---")
    import os
    modules_txt = frappe.get_app_path("gym_management", "modules.txt")
    if os.path.exists(modules_txt):
        print(open(modules_txt).read())
    else:
        print("  modules.txt not found at", modules_txt)

    print()
    print("DONE.")
