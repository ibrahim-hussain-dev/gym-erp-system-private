import frappe

def run():
    doc = frappe.get_doc("Client Script", "Gym Member")
    print("----- SCRIPT START -----")
    print(doc.script)
    print("----- SCRIPT END -----")
