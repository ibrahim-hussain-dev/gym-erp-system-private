import frappe
import json

def run():
    print("=" * 60)
    print("GYM MEMBER - FULL FIELD LIST (for reference)")
    print("=" * 60)
    meta = frappe.get_meta("Gym Member")
    for f in meta.fields:
        print(f"{f.fieldname} | {f.label} | {f.fieldtype}")

    print()
    print("=" * 60)
    print("DOES 'Gym Invoice' DOCTYPE EXIST?")
    print("=" * 60)
    print(frappe.db.exists("DocType", "Gym Invoice"))

    print()
    print("=" * 60)
    print("DISABLING legacy Client Script + Server Script on Gym Member")
    print("=" * 60)

    cs_list = frappe.get_all("Client Script", filters={"dt": "Gym Member"}, fields=["name"])
    for cs in cs_list:
        frappe.db.set_value("Client Script", cs.name, "disabled", 1)
        print(f"Disabled Client Script: {cs.name}")

    ss_list = frappe.get_all("Server Script", filters={"reference_doctype": "Gym Member"}, fields=["name"])
    for ss in ss_list:
        frappe.db.set_value("Server Script", ss.name, "disabled", 1)
        print(f"Disabled Server Script: {ss.name}")

    frappe.db.commit()

    print()
    print("=" * 60)
    print("PATCHING FIXTURE JSON FILES so 'bench migrate' doesn't re-enable them")
    print("=" * 60)
    for path in [
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/fixtures/client_script.json",
        "/home/frappe/frappe-bench/apps/gym_management/gym_management/fixtures/server_script.json",
    ]:
        with open(path) as f:
            records = json.load(f)
        changed = False
        for r in records:
            if r.get("dt") == "Gym Member" or r.get("reference_doctype") == "Gym Member":
                r["disabled"] = 1
                changed = True
        if changed:
            with open(path, "w") as f:
                json.dump(records, f, indent=1)
            print(f"Patched: {path}")
        else:
            print(f"No matching record found in: {path}")

    print("DONE")
