frappe.pages['sell-membership'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Sell / Renew Membership',
        single_column: true
    });
    page.set_primary_action('New Sale', () => open_sell_dialog(), 'add');
    open_sell_dialog();
    function open_sell_dialog() {
        let dialog = new frappe.ui.Dialog({
            title: 'Sell / Renew Membership',
            size: 'extra-large',
            secondary_action_label: 'Back',
            secondary_action: () => {
                dialog.set_value('step', 1);
                update_wizard_buttons(dialog);
            },
            fields: [
                {
                    fieldname: 'is_new_member',
                    fieldtype: 'Check',
                    label: 'New Member (not registered yet)',
                    default: 0,
                    onchange: () => {
                        dialog.set_value('step', 1);
                        update_wizard_buttons(dialog);
                        refresh_billing_preview(dialog);
                    }
                },
                {
                    fieldname: 'member',
                    fieldtype: 'Link',
                    label: 'Gym Member',
                    options: 'Gym Member',
                    description: 'Search by phone, CNIC, or name',
                    depends_on: 'eval:!doc.is_new_member',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'step',
                    fieldtype: 'Int',
                    hidden: 1,
                    default: 1
                },
                {
                    fieldname: 'section_break_member_details',
                    fieldtype: 'Section Break',
                    label: 'Member Details',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'full_name',
                    fieldtype: 'Data',
                    label: 'Full Name',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'phone',
                    fieldtype: 'Data',
                    label: 'Phone',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'col_break_member1',
                    fieldtype: 'Column Break',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'email',
                    fieldtype: 'Data',
                    label: 'Email',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'national_id_cnic',
                    fieldtype: 'Data',
                    label: 'CNIC',
                    depends_on: 'eval:doc.is_new_member && doc.step==1',
                    onchange: () => format_cnic(dialog)
                },
                {
                    fieldname: 'section_break_fitness_profile',
                    fieldtype: 'Section Break',
                    label: 'Fitness Profile',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'gender',
                    fieldtype: 'Select',
                    label: 'Gender',
                    options: '\nMale\nFemale\nOther',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'height_cm',
                    fieldtype: 'Float',
                    label: 'Height (cm)',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'weight_kg',
                    fieldtype: 'Float',
                    label: 'Weight (kg)',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'col_break_fitness1',
                    fieldtype: 'Column Break',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'fitness_goal',
                    fieldtype: 'Select',
                    label: 'Fitness Goal',
                    options: '\nWeight Loss\nMuscle Gain\nGeneral Fitness\nRehab\nOther',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'preferred_workout_time',
                    fieldtype: 'Select',
                    label: 'Preferred Workout Time',
                    options: '\nMorning\nAfternoon\nEvening\nAny',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'medical_conditions',
                    fieldtype: 'Small Text',
                    label: 'Medical Conditions / Notes',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'section_break_emergency',
                    fieldtype: 'Section Break',
                    label: 'Emergency Contact',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'emergency_contact_name',
                    fieldtype: 'Data',
                    label: 'Emergency Contact Name',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'col_break_emergency1',
                    fieldtype: 'Column Break',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'emergency_contact_phone',
                    fieldtype: 'Data',
                    label: 'Emergency Contact Phone',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'section_break_plans',
                    fieldtype: 'Section Break',
                    label: 'Plans',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'plans',
                    fieldtype: 'MultiSelectPills',
                    label: 'Plans (select Registration + Membership + any add-ons together)',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    get_data: function(txt) {
                        return frappe.db.get_list('Gym Plan', {
                            filters: { disabled: 0 },
                            fields: ['name'],
                            limit: 20
                        }).then(data => data.map(d => d.name));
                    },
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'package',
                    fieldtype: 'Link',
                    label: 'Package / Bundle (optional \u2014 auto-adds all its services)',
                    options: 'Gym Package',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    get_query: () => ({ filters: { disabled: 0 } }),
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'mode',
                    fieldtype: 'Select',
                    label: 'Billing Mode',
                    options: 'One-Time / Package\nPay in Advance',
                    default: 'One-Time / Package',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'periods',
                    fieldtype: 'Int',
                    label: 'Number of Periods',
                    description: 'Multiplies each selected plan\'s own duration (e.g. 3 \u00d7 a 1-Week plan = 3 weeks; 6 \u00d7 a 1-Month plan = 6 months; 3 \u00d7 a 2-Day pass = 6 days).',
                    default: 1,
                    depends_on: 'eval:(!doc.is_new_member || doc.step==2) && doc.mode=="Pay in Advance"',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'promo_code',
                    fieldtype: 'Data',
                    label: 'Promo Code (optional)',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'auto_renew',
                    fieldtype: 'Check',
                    label: 'Auto-Renew this membership when it expires',
                    default: 0,
                    description: 'When the membership expires, a new invoice will be generated automatically and the membership will continue.',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'billing_section',
                    fieldtype: 'Section Break',
                    label: 'Billing',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'billing_preview',
                    fieldtype: 'HTML',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'total_amount',
                    fieldtype: 'Currency',
                    label: 'Total Amount (after discount)',
                    read_only: 1,
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'col_break_billing',
                    fieldtype: 'Column Break',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'amount_received',
                    fieldtype: 'Currency',
                    label: 'Amount Received Now',
                    default: 0,
                    description: 'Defaults to the full total. Reduce it for a partial / installment payment.',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'mode_of_payment',
                    fieldtype: 'Link',
                    label: 'Mode of Payment',
                    options: 'Mode of Payment',
                    default: 'Cash',
                    depends_on: 'eval:(!doc.is_new_member || doc.step==2) && doc.amount_received > 0'
                },
                {
                    fieldname: 'payment_due_date',
                    fieldtype: 'Date',
                    label: 'Due Date for Remaining Balance',
                    depends_on: 'eval:(!doc.is_new_member || doc.step==2) && doc.total_amount && doc.amount_received < doc.total_amount'
                }
            ],
            primary_action_label: 'Complete Sale',
            primary_action: (values) => complete_sale(dialog, values)
        });
        dialog.custom_discounts = {};
        dialog.show();
        dialog.$wrapper.find('.modal-dialog').css({ 'max-width': '1100px', 'width': '95%' });
        update_wizard_buttons(dialog);
    }
    function format_cnic(dialog) {
        let value = dialog.get_value('national_id_cnic') || '';
        let digits = value.replace(/[^0-9]/g, '').slice(0, 13);
        let formatted = digits;
        if (digits.length > 5) {
            formatted = digits.slice(0, 5) + '-' + digits.slice(5, 12) + (digits.length > 12 ? '-' + digits.slice(12) : '');
        }
        if (formatted !== value) {
            dialog.set_value('national_id_cnic', formatted);
        }
    }
    function update_wizard_buttons(dialog) {
        let is_new = dialog.get_value('is_new_member');
        let step = dialog.get_value('step') || 1;
        let $secondary = dialog.$wrapper.find('.btn-secondary');
        if (is_new && step == 1) {
            dialog.set_primary_action('Next \u2192', (values) => go_to_step_2(dialog, values));
            $secondary.hide();
        } else if (is_new && step == 2) {
            dialog.set_primary_action('Save Member & Generate Bill', (values) => complete_sale(dialog, values));
            $secondary.show().text('\u2190 Back');
        } else {
            dialog.set_primary_action('Complete Sale', (values) => complete_sale(dialog, values));
            $secondary.hide();
        }
    }
    function go_to_step_2(dialog, values) {
        if (!values.full_name || !values.phone || !values.email) {
            frappe.msgprint('Full Name, Phone, and Email are required to continue.');
            return;
        }
        dialog.set_value('step', 2);
        update_wizard_buttons(dialog);
    }
    function complete_sale(dialog, values) {
        if (!values.is_new_member && !values.member) {
            frappe.msgprint('Select an existing Gym Member or check "New Member".');
            return;
        }
        if (values.is_new_member && (!values.full_name || !values.phone || !values.email)) {
            frappe.msgprint('Full Name, Phone, and Email are required for a new member.');
            return;
        }
        if ((!values.plans || !values.plans.length) && !values.package) {
            frappe.msgprint('Select at least one plan or a package.');
            return;
        }
        if (values.mode == 'Pay in Advance' && (!values.periods || values.periods < 1)) {
            frappe.msgprint('Number of Periods must be at least 1.');
            return;
        }
        frappe.call({
            method: 'gym_management.gym_erp_system.api.sell_membership',
            args: {
                plans: values.plans || [],
                package: values.package,
                member: values.member,
                is_new_member: values.is_new_member,
                full_name: values.full_name,
                phone: values.phone,
                email: values.email,
                national_id_cnic: values.national_id_cnic,
                gender: values.gender,
                height_cm: values.height_cm,
                weight_kg: values.weight_kg,
                fitness_goal: values.fitness_goal,
                preferred_workout_time: values.preferred_workout_time,
                medical_conditions: values.medical_conditions,
                emergency_contact_name: values.emergency_contact_name,
                emergency_contact_phone: values.emergency_contact_phone,
                mode: values.mode,
                periods: values.periods,
                discounts: JSON.stringify(dialog.custom_discounts || {}),
                amount_received: values.amount_received,
                mode_of_payment: values.mode_of_payment,
                payment_due_date: values.payment_due_date,
                auto_renew: values.auto_renew,
                promo_code: values.promo_code
            },
            freeze: true,
            freeze_message: 'Processing sale...',
            callback: function(r) {
                if (r.message) {
                    dialog.hide();
                    let outstanding = r.message.outstanding_amount;
                    let payment_line = outstanding > 0
                        ? `Outstanding: Rs ${outstanding}${r.message.due_date ? ' (Due: ' + r.message.due_date + ')' : ''}`
                        : 'Fully Paid';
                    frappe.msgprint({
                        title: 'Sale Complete',
                        indicator: outstanding > 0 ? 'orange' : 'green',
                        message: `Invoice <b>${r.message.invoice}</b> created. Grand Total: Rs ${r.message.grand_total}. ${payment_line}`
                    });
                    frappe.set_route('Form', 'Sales Invoice', r.message.invoice);
                }
            }
        });
    }
    function refresh_billing_preview(dialog) {
        let plans = dialog.get_value('plans');
        let package_name = dialog.get_value('package');
        if (!dialog.custom_discounts) dialog.custom_discounts = {};
        if ((!plans || !plans.length) && !package_name) {
            dialog.set_value('total_amount', 0);
            dialog.fields_dict.billing_preview.$wrapper.html('');
            return;
        }
        let member = dialog.get_value('is_new_member') ? null : dialog.get_value('member');
        frappe.call({
            method: 'gym_management.gym_erp_system.api.get_billing_preview',
            args: {
                plans: plans || [],
                package: package_name,
                member: member,
                mode: dialog.get_value('mode'),
                periods: dialog.get_value('periods'),
                discounts: JSON.stringify(dialog.custom_discounts),
                promo_code: dialog.get_value('promo_code')
            },
            callback: function(r) {
                if (!r.message) return;
                let valid_keys = r.message.lines.map(l => l.key);
                Object.keys(dialog.custom_discounts).forEach(k => {
                    if (!valid_keys.includes(k)) delete dialog.custom_discounts[k];
                });
                let total = r.message.total_amount;
                dialog.set_value('total_amount', total);
                dialog.set_value('amount_received', total);
                let promo_msg = '';
                if (r.message.promo) {
                    let color = r.message.promo.valid ? '#2e7d32' : '#c62828';
                    promo_msg = `<div style="color:${color}; margin-bottom:8px;"><b>${r.message.promo.message}</b></div>`;
                }
                let rows = r.message.lines.map(l => {
                    let d = dialog.custom_discounts[l.key] || { type: 'None', value: 0 };
                    let coverage = l.one_time ? 'One-Time Charge' : (frappe.datetime.str_to_user(l.start_date) + ' &rarr; ' + frappe.datetime.str_to_user(l.end_date));
                    return `
                    <tr data-key="${l.key}">
                        <td style="white-space:nowrap;">${l.plan}<br><span class="text-muted small">${coverage}</span></td>
                        <td style="text-align:right; white-space:nowrap;">Rs ${format_currency(l.gross_amount)}</td>
                        <td style="min-width:120px;">
                            <select class="form-control discount-type">
                                <option value="None" ${d.type=='None'?'selected':''}>No Discount</option>
                                <option value="Percentage" ${d.type=='Percentage'?'selected':''}>%</option>
                                <option value="Fixed Amount" ${d.type=='Fixed Amount'?'selected':''}>Rs Fixed</option>
                            </select>
                        </td>
                        <td style="min-width:100px;">
                            <input type="number" class="form-control discount-value" min="0" value="${d.value || ''}" ${d.type=='None'?'disabled':''}>
                        </td>
                        <td style="text-align:right; white-space:nowrap;"><b>Rs ${format_currency(l.amount)}</b></td>
                    </tr>`;
                }).join('');
                dialog.fields_dict.billing_preview.$wrapper.html(promo_msg + `
                    <div style="overflow-x:auto;">
                        <table class="table table-bordered" style="margin-bottom: 10px; min-width: 650px;">
                            <thead>
                                <tr><th>Plan</th><th style="text-align:right">Gross</th><th>Discount</th><th>Value</th><th style="text-align:right">Net Amount</th></tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                `);
                dialog.fields_dict.billing_preview.$wrapper.find('tr[data-key]').each(function() {
                    let $row = $(this);
                    let key = $row.attr('data-key');
                    $row.find('.discount-type').on('change', function() {
                        let type = $(this).val();
                        if (!dialog.custom_discounts[key]) dialog.custom_discounts[key] = { type: 'None', value: 0 };
                        dialog.custom_discounts[key].type = type;
                        if (type == 'None') dialog.custom_discounts[key].value = 0;
                        refresh_billing_preview(dialog);
                    });
                    $row.find('.discount-value').on('change', function() {
                        let val = flt($(this).val());
                        if (!dialog.custom_discounts[key]) dialog.custom_discounts[key] = { type: 'None', value: 0 };
                        dialog.custom_discounts[key].value = val;
                        refresh_billing_preview(dialog);
                    });
                });
            }
        });
    }
};
