frappe.ui.form.on('Gym Member', {
    onload: function(frm) {
        if (frm.is_new()) {
            if (!frm.doc.membership_status) frm.set_value('membership_status', 'Active');
            if (!frm.doc.joining_date) frm.set_value('joining_date', frappe.datetime.get_today());
        }
    },

    // CNIC Auto-Formatter (XXXXX-XXXXXXX-X)
    national_id_cnic: function(frm) {
        if (!frm.doc.national_id_cnic) return;
        let raw = frm.doc.national_id_cnic.replace(/\D/g, '').substring(0, 13);
        let formatted = raw;
        if (raw.length > 12) formatted = `${raw.substring(0, 5)}-${raw.substring(5, 12)}-${raw.substring(12, 13)}`;
        else if (raw.length > 5) formatted = `${raw.substring(0, 5)}-${raw.substring(5, 12)}`;
        if (frm.doc.national_id_cnic !== formatted) frm.set_value('national_id_cnic', formatted);
    }
});
