import frappe
import subprocess

def run():
    print("=" * 60)
    print("GYM MEMBER DOCTYPE - ALL FIELDS (looking for freeze-related ones)")
    print("=" * 60)
    meta = frappe.get_meta("Gym Member")
    for f in meta.fields:
        if "freeze" in f.fieldname.lower() or "status" in f.fieldname.lower() or "subscription" in f.fieldname.lower():
            print(f"fieldname={f.fieldname} | label={f.label} | fieldtype={f.fieldtype} | options={f.options}")

    print()
    print("=" * 60)
    print("GYM SUBSCRIPTION DOCTYPE - ALL FIELDS (freeze may live here instead)")
    print("=" * 60)
    if frappe.db.exists("DocType", "Gym Subscription"):
        meta2 = frappe.get_meta("Gym Subscription")
        for f in meta2.fields:
            print(f"fieldname={f.fieldname} | label={f.label} | fieldtype={f.fieldtype} | options={f.options}")
    else:
        print("Gym Subscription doctype not found")

    print()
    print("=" * 60)
    print("WHERE IS 'freeze_start_date' REFERENCED IN CODE?")
    print("=" * 60)
    out = subprocess.run(["grep", "-rn", "freeze_start_date", "/home/frappe/frappe-bench/apps/gym_management/"], capture_output=True, text=True)
    print(out.stdout or "NOT FOUND ANYWHERE IN CODE")

    print()
    print("=" * 60)
    print("WHERE IS 'freeze' REFERENCED GENERALLY? (all matches)")
    print("=" * 60)
    out2 = subprocess.run(["grep", "-rln", "-i", "freeze", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/"], capture_output=True, text=True)
    print(out2.stdout)

    print()
    print("=" * 60)
    print("manage_subscription PAGE FILES (Freeze/Resume Membership page)")
    print("=" * 60)
    out3 = subprocess.run(["find", "/home/frappe/frappe-bench/apps/gym_management", "-iname", "*manage_subscription*"], capture_output=True, text=True)
    print(out3.stdout)
    for f in out3.stdout.strip().split("\n"):
        if f and (f.endswith(".py") or f.endswith(".js")):
            print(f"--- {f} ---")
            print(subprocess.run(["cat", f], capture_output=True, text=True).stdout)

    print()
    print("=" * 60)
    print("ANY CLIENT SCRIPT / SERVER SCRIPT MENTIONING freeze?")
    print("=" * 60)
    for dt in ["Client Script", "Server Script"]:
        rows = frappe.get_all(dt, filters={"dt": "Gym Member"}, fields=["name"])
        for r in rows:
            doc = frappe.get_doc(dt, r.name)
            content = getattr(doc, "script", "") or getattr(doc, "code", "") or ""
            if "freeze" in content.lower():
                print(f"{dt}: {r.name}")
                print(content)
                print("---")
