frappe.pages['book-pt-session'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Book PT Session',
        single_column: true
    });
    page.set_primary_action('Book Session', () => open_booking_dialog(), 'add');
    open_booking_dialog();

    function open_booking_dialog() {
        let dialog = new frappe.ui.Dialog({
            title: 'Book PT Session',
            fields: [
                {
                    fieldname: 'member',
                    fieldtype: 'Link',
                    label: 'Member',
                    options: 'Gym Member',
                    reqd: 1,
                    description: 'Search by phone, CNIC, or name'
                },
                {
                    fieldname: 'gym_subscription',
                    fieldtype: 'Link',
                    label: 'PT Subscription (sessions pack)',
                    options: 'Gym Subscription',
                    reqd: 1,
                    get_query: () => {
                        return {
                            filters: {
                                member: dialog.get_value('member'),
                                status: ['in', ['Active', 'Scheduled']]
                            }
                        };
                    }
                },
                {
                    fieldname: 'col_break_1',
                    fieldtype: 'Column Break'
                },
                {
                    fieldname: 'trainer',
                    fieldtype: 'Link',
                    label: 'Trainer',
                    options: 'Gym Trainer',
                    reqd: 1,
                    get_query: () => ({ filters: { disabled: 0 } }),
                    onchange: () => refresh_windows(dialog)
                },
                {
                    fieldname: 'date',
                    fieldtype: 'Date',
                    label: 'Session Date',
                    reqd: 1,
                    default: frappe.datetime.get_today(),
                    onchange: () => refresh_windows(dialog)
                },
                {
                    fieldname: 'section_break_1',
                    fieldtype: 'Section Break',
                    label: 'Available Time Windows'
                },
                {
                    fieldname: 'window',
                    fieldtype: 'Select',
                    label: 'Pick a Time Window',
                    options: ''
                }
            ],
            primary_action_label: 'Book Session',
            primary_action: (values) => {
                if (!values.window) {
                    frappe.msgprint('Select a time window (trainer must be available that day).');
                    return;
                }
                let parts = values.window.split(' - ');
                frappe.call({
                    method: 'gym_management.gym_erp_system.api.book_pt_slot',
                    args: {
                        member: values.member,
                        gym_subscription: values.gym_subscription,
                        trainer: values.trainer,
                        date: values.date,
                        start_time: parts[0],
                        end_time: parts[1]
                    },
                    freeze: true,
                    freeze_message: 'Booking session...',
                    callback: function(r) {
                        if (r.message) {
                            dialog.hide();
                            frappe.msgprint({
                                title: 'Session Booked',
                                indicator: 'green',
                                message: `Gym Slot <b>${r.message}</b> booked successfully.`
                            });
                        }
                    }
                });
            }
        });
        dialog.show();
    }

    function refresh_windows(dialog) {
        let trainer = dialog.get_value('trainer');
        let date = dialog.get_value('date');
        if (!trainer || !date) return;
        frappe.call({
            method: 'gym_management.gym_erp_system.api.get_trainer_windows',
            args: { trainer: trainer, date: date },
            callback: function(r) {
                let windows = r.message || [];
                let options = windows.map(w => `${w.start_time} - ${w.end_time}`);
                dialog.set_df_property('window', 'options', options.join('\n'));
                dialog.set_value('window', options.length === 1 ? options[0] : '');
                dialog.refresh_field('window');
                if (!options.length) {
                    frappe.msgprint('This trainer has no declared availability on the selected day.');
                }
            }
        });
    }
};
