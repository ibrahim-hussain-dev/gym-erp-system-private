frappe.pages['manage-subscription'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Freeze / Resume Membership',
        single_column: true
    });
    page.set_primary_action('Open', () => open_dialog(), 'add');
    open_dialog();

    function open_dialog() {
        let dialog = new frappe.ui.Dialog({
            title: 'Freeze / Resume Membership',
            size: 'large',
            fields: [
                {
                    fieldname: 'member',
                    fieldtype: 'Link',
                    label: 'Gym Member',
                    options: 'Gym Member',
                    description: 'Search by phone, CNIC, or name',
                    onchange: () => refresh_subscriptions(dialog)
                },
                {
                    fieldname: 'subscriptions_html',
                    fieldtype: 'HTML'
                }
            ]
        });
        dialog.show();
    }

    function refresh_subscriptions(dialog) {
        let member = dialog.get_value('member');
        if (!member) {
            dialog.fields_dict.subscriptions_html.$wrapper.html('');
            return;
        }
        frappe.call({
            method: 'gym_management.gym_erp_system.api.get_member_subscriptions',
            args: { member: member },
            callback: function(r) {
                let rows = (r.message || []).map(s => {
                    if (s.status === 'Frozen') {
                        return `
                        <tr>
                            <td>${s.gym_plan}</td>
                            <td>${s.status}</td>
                            <td>${frappe.datetime.str_to_user(s.start_date)} &rarr; ${frappe.datetime.str_to_user(s.end_date)}</td>
                            <td>
                                <button class="btn btn-xs btn-primary btn-resume" data-sub="${s.name}">Resume</button>
                            </td>
                        </tr>`;
                    }
                    return `
                    <tr>
                        <td>${s.gym_plan}</td>
                        <td>${s.status}</td>
                        <td>${frappe.datetime.str_to_user(s.start_date)} &rarr; ${frappe.datetime.str_to_user(s.end_date)}</td>
                        <td>
                            <input type="number" class="form-control input-xs freeze-days" data-sub="${s.name}" placeholder="Days" style="width:80px; display:inline-block;">
                            <button class="btn btn-xs btn-warning btn-freeze" data-sub="${s.name}">Freeze</button>
                        </td>
                    </tr>`;
                }).join('');

                dialog.fields_dict.subscriptions_html.$wrapper.html(`
                    <div style="overflow-x:auto;">
                        <table class="table table-bordered" style="margin-top: 10px;">
                            <thead>
                                <tr><th>Plan</th><th>Status</th><th>Coverage</th><th>Action</th></tr>
                            </thead>
                            <tbody>${rows || '<tr><td colspan="4">No active/frozen subscriptions found.</td></tr>'}</tbody>
                        </table>
                    </div>
                `);

                dialog.fields_dict.subscriptions_html.$wrapper.find('.btn-freeze').on('click', function() {
                    let sub = $(this).data('sub');
                    let days = dialog.fields_dict.subscriptions_html.$wrapper.find(`.freeze-days[data-sub="${sub}"]`).val();
                    if (!days || days <= 0) {
                        frappe.msgprint('Enter number of days to freeze.');
                        return;
                    }
                    frappe.call({
                        method: 'gym_management.gym_erp_system.gym_subscription.freeze_subscription',
                        args: { subscription: sub, freeze_days: days },
                        freeze: true,
                        freeze_message: 'Freezing...',
                        callback: function() {
                            frappe.show_alert({ message: 'Subscription frozen.', indicator: 'green' });
                            refresh_subscriptions(dialog);
                        }
                    });
                });

                dialog.fields_dict.subscriptions_html.$wrapper.find('.btn-resume').on('click', function() {
                    let sub = $(this).data('sub');
                    frappe.call({
                        method: 'gym_management.gym_erp_system.gym_subscription.resume_subscription',
                        args: { subscription: sub },
                        freeze: true,
                        freeze_message: 'Resuming...',
                        callback: function() {
                            frappe.show_alert({ message: 'Subscription resumed.', indicator: 'green' });
                            refresh_subscriptions(dialog);
                        }
                    });
                });
            }
        });
    }
};
