import frappe

def run():
    email_id = "iibrahimhere@gmail.com"
    app_password = "lfvibjtbnncbadnv"

    if frappe.db.exists("Email Account", email_id):
        acc = frappe.get_doc("Email Account", email_id)
    else:
        acc = frappe.new_doc("Email Account")
        acc.email_account_name = "Gym ERP Notifications"
        acc.email_id = email_id

    acc.enable_outgoing = 1
    acc.smtp_server = "smtp.gmail.com"
    acc.smtp_port = 587
    acc.use_tls = 1
    acc.use_ssl = 0
    acc.password = app_password
    acc.default_outgoing = 1
    acc.always_use_account_email_id_as_sender = 1

    if acc.is_new():
        acc.insert(ignore_permissions=True)
    else:
        acc.save(ignore_permissions=True)

    frappe.db.commit()
    print("Email Account saved:", acc.name, "| enable_outgoing:", acc.enable_outgoing, "| default_outgoing:", acc.default_outgoing)
    print("DONE")
