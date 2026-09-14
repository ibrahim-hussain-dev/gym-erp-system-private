import frappe

def run():
    print("=" * 60)
    print("1. Gym Subscription DOCTYPE FORM SCRIPT (gym_subscription.js) - kya buttons hain?")
    print("=" * 60)
    import subprocess
    out = subprocess.run(["cat", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/doctype/gym_subscription/gym_subscription.js"], capture_output=True, text=True)
    print(out.stdout or "(file empty or not found)")

    print()
    print("=" * 60)
    print("2. ANY OTHER Client Script attached to Gym Subscription?")
    print("=" * 60)
    rows = frappe.get_all("Client Script", filters={"dt": "Gym Subscription"}, fields=["name", "enabled"])
    print(rows)
    for r in rows:
        doc = frappe.get_doc("Client Script", r.name)
        print(f"--- {r.name} (enabled={r.enabled}) ---")
        print(doc.script)

    print()
    print("=" * 60)
    print("3. CURRENT Gym Member Client Script content (kya abhi live hai)")
    print("=" * 60)
    rows2 = frappe.get_all("Client Script", filters={"dt": "Gym Member"}, fields=["name", "enabled"])
    print(rows2)
    for r in rows2:
        doc = frappe.get_doc("Client Script", r.name)
        print(f"--- {r.name} (enabled={r.enabled}) ---")
        print(doc.script)

    print()
    print("=" * 60)
    print("4. Server Script status on Gym Member")
    print("=" * 60)
    rows3 = frappe.get_all("Server Script", filters={"reference_doctype": "Gym Member"}, fields=["name", "disabled"])
    print(rows3)

    print()
    print("=" * 60)
    print("5. Page 'manage-subscription' status")
    print("=" * 60)
    print("exists:", frappe.db.exists("Page", "manage-subscription"))

    print()
    print("=" * 60)
    print("6. gym_subscription.py - confirm freeze/resume/cancel functions still intact")
    print("=" * 60)
    out2 = subprocess.run(["grep", "-n", "def freeze_subscription\|def resume_subscription\|def cancel_subscription\|def get_member_subscriptions", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/gym_subscription.py"], capture_output=True, text=True)
    print(out2.stdout)
    out3 = subprocess.run(["grep", "-n", "def get_member_subscriptions", "/home/frappe/frappe-bench/apps/gym_management/gym_management/gym_erp_system/api.py"], capture_output=True, text=True)
    print(out3.stdout)
