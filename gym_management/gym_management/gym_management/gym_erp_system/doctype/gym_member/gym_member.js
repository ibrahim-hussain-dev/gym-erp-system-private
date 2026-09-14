frappe.ui.form.on('Gym Member', {
    onload: function(frm) {
        if (frm.is_new()) {
            if (!frm.doc.membership_status) frm.set_value('membership_status', 'Active');
            if (!frm.doc.joining_date) frm.set_value('joining_date', frappe.datetime.get_today());
        }
        set_timing_slot_filters(frm);
    },

    gender: function(frm) {
        set_timing_slot_filters(frm);
        clear_invalid_slot(frm, 'preferred_workout_time');
        clear_invalid_slot(frm, 'alternative_workout_time');
    },

    national_id_cnic: function(frm) {
        if (!frm.doc.national_id_cnic) return;
        let raw = frm.doc.national_id_cnic.replace(/\D/g, '').substring(0, 13);
        let formatted = raw;
        if (raw.length > 12) formatted = `${raw.substring(0, 5)}-${raw.substring(5, 12)}-${raw.substring(12, 13)}`;
        else if (raw.length > 5) formatted = `${raw.substring(0, 5)}-${raw.substring(5, 12)}`;
        if (frm.doc.national_id_cnic !== formatted) frm.set_value('national_id_cnic', formatted);
    }
});

function set_timing_slot_filters(frm) {
    let query = function() {
        let allowed = ['Mixed'];
        if (frm.doc.gender === 'Female') allowed.push('Female');
        else if (frm.doc.gender === 'Male') allowed.push('Male');
        else allowed.push('Male', 'Female');
        return { filters: { gender: ['in', allowed], disabled: 0 } };
    };
    frm.set_query('preferred_workout_time', query);
    frm.set_query('alternative_workout_time', query);
}

function clear_invalid_slot(frm, fieldname) {
    if (!frm.doc[fieldname] || !frm.doc.gender) return;
    frappe.db.get_value('Gym Timing Slot', frm.doc[fieldname], 'gender').then(r => {
        let slot_gender = r.message && r.message.gender;
        if (slot_gender && slot_gender !== 'Mixed' && slot_gender !== frm.doc.gender) {
            frm.set_value(fieldname, '');
            frappe.show_alert({ message: 'Cleared \u2014 selected slot no longer matches gender.', indicator: 'orange' });
        }
    });
}
