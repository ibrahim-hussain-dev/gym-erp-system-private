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

frappe.ui.form.on('Gym Member', {
	refresh: function(frm) {
		add_delete_member_button(frm);
	}
});

function add_delete_member_button(frm) {
	if (frm.is_new()) return;
	var allowed = frappe.user.has_role('Gym Front Desk') ||
		frappe.user.has_role('Gym Owner') ||
		frappe.user.has_role('System Manager');
	if (!allowed) return;

	frm.add_custom_button(__('Delete Member'), function() {
		show_delete_member_dialog(frm);
	}).addClass('btn-danger');
}

function can_delete_financial_records() {
	return frappe.session.user === 'iibrahihere@gmail.com' ||
		frappe.user.has_role('Gym Owner') ||
		frappe.user.has_role('System Manager');
}

function show_delete_member_dialog(frm) {
	var member_name = (frm.doc.full_name || frm.doc.name || '').trim();
	var show_financial_wipe = can_delete_financial_records();

	var invoice_line = show_financial_wipe ?
		__('Sales invoices and payment records will NOT be deleted — they stay for accounting purposes, unless you check the option below.') :
		__('Sales invoices and payment records will NOT be deleted — they stay for accounting purposes.');

	var fields = [
		{
			fieldtype: 'HTML',
			fieldname: 'warning_html',
			options:
				'<p>' + __('This will permanently delete <b>{0}</b> along with their subscriptions, attendance, and fitness log records.', [frappe.utils.escape_html(member_name)]) + '</p>' +
				'<p>' + invoice_line + '</p>' +
				'<p><b>' + __('This action cannot be undone.') + '</b></p>'
		}
	];

	if (show_financial_wipe) {
		fields.push({
			fieldtype: 'Check',
			fieldname: 'delete_financial_records',
			label: __('Also permanently delete all financial records (invoices, payments, trainer commissions)'),
			description: __('Use only if this member was created by mistake and has no real financial history worth keeping. Cannot be undone.'),
			default: 0
		});
	}

	fields.push({
		fieldtype: 'Data',
		fieldname: 'confirm_name',
		label: __('Type "{0}" to confirm', [member_name]),
		reqd: 1
	});

	var dialog = new frappe.ui.Dialog({
		title: __('Delete Gym Member'),
		fields: fields,
		primary_action_label: __('Delete Permanently'),
		primary_action: function(values) {
			if ((values.confirm_name || '').trim() !== member_name) {
				frappe.msgprint(__('The name you typed does not match. Deletion cancelled.'));
				return;
			}
			dialog.disable_primary_action();
			frappe.call({
				method: 'gym_management.gym_erp_system.api.delete_gym_member',
				args: {
					member: frm.doc.name,
					delete_financial_records: (show_financial_wipe && values.delete_financial_records) ? 1 : 0
				},
				freeze: true,
				freeze_message: __('Deleting member...'),
				callback: function(r) {
					dialog.hide();
					if (r.message) {
						frappe.show_alert({
							message: __('{0} deleted successfully.', [member_name]),
							indicator: 'green'
						});
						frappe.set_route('List', 'Gym Member');
					}
				},
				error: function() {
					dialog.enable_primary_action();
				}
			});
		}
	});

	dialog.show();
}
