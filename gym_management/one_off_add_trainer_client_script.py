import frappe

def run():
    if frappe.db.exists("Client Script", {"dt": "Gym Trainer", "view": "Form"}):
        print("Client Script already exists, skipping.")
        return
    script = """
frappe.ui.form.on('Gym Trainer', {
    refresh: function(frm) {
        if (frm.doc.name) {
            frappe.call({
                method: 'gym_management.gym_erp_system.api.get_trainer_commission_stats',
                args: { trainer: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frm.doc.sessions_attended = r.message.sessions_attended;
                        frm.doc.total_commission = r.message.total_commission;
                        frm.refresh_field('sessions_attended');
                        frm.refresh_field('total_commission');
                    }
                }
            });
        }
    }
});
"""
    doc = frappe.get_doc({
        "doctype": "Client Script",
        "name": "Gym Trainer-Form-Commission",
        "dt": "Gym Trainer",
        "view": "Form",
        "enabled": 1,
        "script": script,
    })
    doc.flags.ignore_permissions = True
    doc.insert()
    frappe.db.commit()
    print("Created Client Script for Gym Trainer.")
