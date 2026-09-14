import frappe

def run():
    all_modules = frappe.get_all("Module Def", pluck="name")
    keep_module = "Gym-ERP-System"
    block_list = [m for m in all_modules if m != keep_module]
    print("Modules that will be hidden:", block_list)

    for email in ["owner@gym.local", "fd1@gym.local"]:
        user = frappe.get_doc("User", email)
        user.set("block_modules", [])
        for m in block_list:
            user.append("block_modules", {"module": m})
        user.save(ignore_permissions=True)
        print(email, "-> other modules blocked, only Gym-ERP-System left visible")

    frappe.clear_cache()
    frappe.db.commit()
    print("DONE")
