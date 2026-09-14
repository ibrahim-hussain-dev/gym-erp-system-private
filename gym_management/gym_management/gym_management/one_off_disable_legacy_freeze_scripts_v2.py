import frappe
import json

def toggle_off(doctype, name):
    meta = frappe.get_meta(doctype)
    if meta.get_field("enabled"):
        frappe.db.set_value(doctype, name, "enabled", 0)
        print(f"{doctype} {name}: set enabled=0")
    elif meta.get_field("disabled"):
        frappe.db.set_value(doctype, name, "disabled", 1)
        print(f"{doctype} {name}: set disabled=1")
    else:
        print(f"WARNING: no enabled/disabled field found on {doctype} — could not toggle")

def run():
    cs_list = frappe.get_all("Client Script", filters={"dt": "Gym Member"}, fields=["name"])
    for cs in cs_list:
        toggle_off("Client Script", cs.name)

    ss_list = frappe.get_all("Server Script", filters={"reference_doctype": "Gym Member"}, fields=["name"])
    for ss in ss_list:
        toggle_off("Server Script", ss.name)

    frappe.db.commit()

    print()
    print("=" * 60)
    print("PATCHING FIXTURE JSON FILES")
    print("=" * 60)
    patch_map = {
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/fixtures/client_script.json": ("dt", "enabled", 0),
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/fixtures/server_script.json": ("reference_doctype", "disabled", 1),
    }
    for path, (match_field, toggle_field, toggle_value) in patch_map.items():
        with open(path) as f:
            records = json.load(f)
        changed = False
        for r in records:
            if r.get(match_field) == "Gym Member":
                r[toggle_field] = toggle_value
                changed = True
        if changed:
            with open(path, "w") as f:
                json.dump(records, f, indent=1)
            print(f"Patched: {path} -> {toggle_field}={toggle_value}")
        else:
            print(f"No matching record in: {path}")

    print("DONE")
