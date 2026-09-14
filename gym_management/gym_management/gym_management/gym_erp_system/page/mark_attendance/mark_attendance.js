frappe.pages['mark-attendance'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Mark Attendance',
        single_column: true
    });
    page.set_primary_action('Mark Present', () => open_attendance_dialog(), 'add');
    open_attendance_dialog();

    function open_attendance_dialog() {
        let dialog = new frappe.ui.Dialog({
            title: 'Mark Attendance',
            fields: [
                {
                    fieldname: 'member',
                    fieldtype: 'Link',
                    label: 'Member',
                    options: 'Gym Member',
                    reqd: 1,
                    description: 'Search by phone, CNIC, or name'
                }
            ],
            primary_action_label: 'Mark Present',
            primary_action: (values) => {
                frappe.call({
                    method: 'gym_management.gym_erp_system.api.mark_attendance',
                    args: { member: values.member },
                    freeze: true,
                    freeze_message: 'Marking attendance...',
                    callback: function(r) {
                        if (r.message) {
                            dialog.hide();
                            frappe.show_alert({
                                message: 'Attendance marked. If a PT session was scheduled today, it has been consumed automatically.',
                                indicator: 'green'
                            });
                            open_attendance_dialog();
                        }
                    }
                });
            }
        });
        dialog.show();
    }
};
