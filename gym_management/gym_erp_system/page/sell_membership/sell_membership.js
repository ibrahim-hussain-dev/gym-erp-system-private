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
                    onchange: () => {
                        refresh_billing_preview(dialog);
                        fetch_member_summary(dialog);
                    }
                },
                {
                    fieldname: 'member_summary',
                    fieldtype: 'HTML',
                    depends_on: 'eval:!doc.is_new_member && doc.member'
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
                    depends_on: 'eval:doc.is_new_member && doc.step==1',
                    onchange: () => title_case_words(dialog)
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
                    fieldname: 'member_photo',
                    fieldtype: 'Attach Image',
                    label: 'Member Photo',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'section_break_fitness_profile',
                    fieldtype: 'Section Break',
                    label: 'Fitness Profile',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'activity_level',
                    fieldtype: 'Select',
                    label: 'Activity Level',
                    options: '\nSedentary\nLightly Active\nModerately Active\nVery Active',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'workout_history',
                    fieldtype: 'Select',
                    label: 'Workout History',
                    options: '\nNewbie\nBeginner\nIntermediate\nAdvanced',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'gender',
                    fieldtype: 'Select',
                    label: 'Gender',
                    options: '\nMale\nFemale',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'height_feet',
                    fieldtype: 'Float',
                    label: 'Height (Feet)',
                    description: 'e.g. 5.5 for 5 feet 6 inches',
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
                    fieldtype: 'Link',
                    label: 'Preferred Training Slot',
                    options: 'Gym Timing Slot',
                    depends_on: 'eval:doc.is_new_member && doc.step==1',
                    get_query: () => {
                        let g = dialog.get_value('gender');
                        let allowed = ['Mixed'];
                        if (g === 'Female') allowed.push('Female');
                        else if (g === 'Male') allowed.push('Male');
                        else allowed.push('Male', 'Female');
                        return { filters: { gender: ['in', allowed], disabled: 0 } };
                    }
                },
                {
                    fieldname: 'alternative_workout_time',
                    fieldtype: 'Link',
                    label: 'Alternative Training Slot (optional)',
                    options: 'Gym Timing Slot',
                    description: 'For flexible-schedule members (e.g. office/university) who may attend at a second time.',
                    depends_on: 'eval:doc.is_new_member && doc.step==1',
                    get_query: () => {
                        let g = dialog.get_value('gender');
                        let allowed = ['Mixed'];
                        if (g === 'Female') allowed.push('Female');
                        else if (g === 'Male') allowed.push('Male');
                        else allowed.push('Male', 'Female');
                        return { filters: { gender: ['in', allowed], disabled: 0 } };
                    }
                },
                {
                    fieldname: 'medical_conditions',
                    fieldtype: 'Small Text',
                    label: 'Medical Conditions / Notes',
                    depends_on: 'eval:doc.is_new_member && doc.step==1'
                },
                {
                    fieldname: 'health_issue',
                    fieldtype: 'Small Text',
                    label: 'Health Issue',
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
                            fields: ['name', 'plan_name', 'duration_value', 'duration_unit', 'monthly_fee'],
                            limit: 20
                        }).then(data => data.map(d => ({
                            value: d.name,
                            label: d.plan_name,
                            description: `${d.duration_value} ${d.duration_unit} \u2014 Rs ${format_currency(d.monthly_fee)}`
                        })));
                    },
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'package',
                    fieldtype: 'Link',
                    hidden: 1,
                    label: 'Package / Bundle (optional \u2014 auto-adds all its services)',
                    options: 'Gym Package',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    get_query: () => ({ filters: { disabled: 0 } }),
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
                    fieldname: 'billing_fields_section',
                    fieldtype: 'Section Break',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },
                {
                    fieldname: 'start_date',
                    fieldtype: 'Date',
                    label: 'Start Date (leave blank to auto-calculate)',
                    description: 'Membership duration will count from this date, even if payment is received later. Leave blank to auto-calculate from today or the member\'s last plan expiry.',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'overall_discount_type',
                    fieldtype: 'Select',
                    label: 'Overall Discount',
                    options: 'None\nPercentage\nFixed Amount',
                    default: 'None',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'overall_discount_value',
                    fieldtype: 'Float',
                    label: 'Overall Discount Value',
                    depends_on: 'eval:(!doc.is_new_member || doc.step==2) && doc.overall_discount_type!="None"',
                    onchange: () => refresh_billing_preview(dialog)
                },
                {
                    fieldname: 'col_break_overall_discount',
                    fieldtype: 'Column Break',
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
        dialog.custom_quantities = {};
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
    function title_case_words(dialog) {
        let value = dialog.get_value('full_name') || '';
        let formatted = value.replace(/\w\S*/g, function(word) {
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        });
        if (formatted !== value) {
            dialog.set_value('full_name', formatted);
        }
    }
    function fetch_member_summary(dialog) {
        let member = dialog.get_value('member');
        if (!member) {
            dialog.fields_dict.member_summary.$wrapper.html('');
            return;
        }
        frappe.call({
            method: 'gym_management.gym_erp_system.api.get_member_summary',
            args: { member: member },
            callback: function(r) {
                if (!r.message || !Object.keys(r.message).length) {
                    dialog.fields_dict.member_summary.$wrapper.html('');
                    return;
                }
                let m = r.message;
                let reg_line = m.registration_paid
                    ? '<span class="indicator-pill green">Registration Paid</span>'
                    : '<span class="indicator-pill red">Registration Not Paid</span>';
                let plan_line = m.last_plan_name
                    ? `Last Plan: <b>${m.last_plan_name}</b> \u2014 ${m.last_plan_status} (${m.last_plan_status === 'Expired' ? 'expired' : 'expires'} ${frappe.datetime.str_to_user(m.last_plan_end_date)})`
                    : 'No previous plan on record.';
                dialog.fields_dict.member_summary.$wrapper.html(`
                    <div class="text-muted small" style="margin-bottom: 8px; padding: 8px; background: #f8f8f8; border-radius: 4px;">
                        ${reg_line}<br>${plan_line}
                    </div>
                `);
            }
        });
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
                member_photo: values.member_photo,
                gender: values.gender,
                height_feet: values.height_feet,
                weight_kg: values.weight_kg,
                fitness_goal: values.fitness_goal,
                preferred_workout_time: values.preferred_workout_time,
                alternative_workout_time: values.alternative_workout_time,
                medical_conditions: values.medical_conditions,
                health_issue: values.health_issue,
                emergency_contact_name: values.emergency_contact_name,
                emergency_contact_phone: values.emergency_contact_phone,
                quantities: JSON.stringify(dialog.custom_quantities || {}),
                discounts: JSON.stringify(dialog.custom_discounts || {}),
                amount_received: values.amount_received,
                mode_of_payment: values.mode_of_payment,
                payment_due_date: values.payment_due_date,
                start_date: values.start_date,
                auto_renew: values.auto_renew,
                overall_discount_type: values.overall_discount_type,
                overall_discount_value: values.overall_discount_value,
                activity_level: values.activity_level,
                workout_history: values.workout_history
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
                    let bill_doctype = "Sales Invoice";
                    let bill_name = r.message.invoice;
                    let bill_format = "Gym Customer Bill";
                    let preview_url = frappe.urllib.get_full_url(
                        "/printview?doctype=" + encodeURIComponent(bill_doctype) +
                        "&name=" + encodeURIComponent(bill_name) +
                        "&format=" + encodeURIComponent(bill_format) +
                        "&no_letterhead=1"
                    );
                    let pdf_url = frappe.urllib.get_full_url(
                        "/api/method/frappe.utils.print_format.download_pdf?doctype=" + encodeURIComponent(bill_doctype) +
                        "&name=" + encodeURIComponent(bill_name) +
                        "&format=" + encodeURIComponent(bill_format) +
                        "&no_letterhead=1"
                    );
                    let bill_dialog = new frappe.ui.Dialog({
                        title: 'Customer Bill - ' + bill_name,
                        size: 'small',
                        fields: [
                            {
                                fieldtype: 'HTML',
                                fieldname: 'bill_preview',
                                options: '<iframe id="customer-bill-frame" style="width:100%; height:65vh; border:1px solid #e5e5e5; border-radius:6px; background:#fff;"></iframe>'
                            }
                        ],
                        primary_action_label: 'Download PDF',
                        primary_action: function() {
                            let a = document.createElement('a');
                            a.href = pdf_url;
                            a.target = '_blank';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        },
                        secondary_action_label: 'Print',
                        secondary_action: function() {
                            let frame = bill_dialog.$wrapper.find('#customer-bill-frame')[0];
                            if (frame && frame.contentWindow) {
                                frame.contentWindow.focus();
                                frame.contentWindow.print();
                            }
                        }
                    });
                    bill_dialog.onhide = function() {
                        frappe.set_route('Form', 'Sales Invoice', r.message.invoice);
                    };
                    bill_dialog.show();
                    let bill_frame = bill_dialog.$wrapper.find('#customer-bill-frame')[0];
                    if (bill_frame) {
                        bill_frame.onload = function() {
                            try {
                                let idoc = bill_frame.contentDocument || bill_frame.contentWindow.document;
                                let banner = idoc.querySelector('.action-banner');
                                if (banner) banner.style.display = 'none';
                            } catch (e) {}
                        };
                        bill_frame.src = preview_url;
                    }
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
                quantities: JSON.stringify(dialog.custom_quantities),
                discounts: JSON.stringify(dialog.custom_discounts),
                overall_discount_type: dialog.get_value('overall_discount_type'),
                overall_discount_value: dialog.get_value('overall_discount_value'),
                override_start_date: dialog.get_value('start_date')
            },
            callback: function(r) {
                if (!r.message) return;
                let valid_keys = r.message.lines.map(l => l.key);
                Object.keys(dialog.custom_discounts).forEach(k => {
                    if (!valid_keys.includes(k)) delete dialog.custom_discounts[k];
                });
                Object.keys(dialog.custom_quantities).forEach(k => {
                    if (!valid_keys.includes(k)) delete dialog.custom_quantities[k];
                });
                let total = r.message.total_amount;
                dialog.set_value('total_amount', total);
                dialog.set_value('amount_received', total);
                let rows = r.message.lines.map(l => {
                    let d = dialog.custom_discounts[l.key] || { type: 'None', value: 0 };
                    let coverage = l.one_time ? 'One-Time Charge' : (frappe.datetime.str_to_user(l.start_date) + ' &rarr; ' + frappe.datetime.str_to_user(l.end_date));
                    let qty_val = l.one_time ? 1 : (dialog.custom_quantities[l.key] || 1);
                    let rate_val = l.gross_amount / qty_val;
                    let qty_cell = l.one_time
                        ? '<span class="text-muted">1</span>'
                        : `<input type="number" class="form-control line-qty" min="1" step="1" style="width:70px;" value="${dialog.custom_quantities[l.key] || 1}">`;
                    return `
                    <tr data-key="${l.key}">
                        <td style="white-space:nowrap;">${l.plan}<br><span class="text-muted small">${coverage}</span></td>
                        <td style="text-align:right; white-space:nowrap;">Rs ${format_currency(rate_val)}</td>
                        <td style="width:80px;">${qty_cell}</td>
                        <td style="text-align:right; white-space:nowrap;">Rs ${format_currency(l.gross_amount)}</td>
                        <td style="min-width:110px;">
                            <select class="form-control discount-type">
                                <option value="None" ${d.type=='None'?'selected':''}>No Discount</option>
                                <option value="Percentage" ${d.type=='Percentage'?'selected':''}>%</option>
                                <option value="Fixed Amount" ${d.type=='Fixed Amount'?'selected':''}>Rs Fixed</option>
                            </select>
                        </td>
                        <td style="min-width:90px;">
                            <input type="number" class="form-control discount-value" min="0" value="${d.value || ''}" ${d.type=='None'?'disabled':''}>
                        </td>
                        <td style="text-align:right; white-space:nowrap;"><b>Rs ${format_currency(l.amount)}</b></td>
                    </tr>`;
                }).join('');
                dialog.fields_dict.billing_preview.$wrapper.html(`
                    <div style="overflow-x:auto;">
                        <table class="table table-bordered" style="margin-bottom: 10px; width:100%;">
                            <thead>
                                <tr><th>Plan</th><th style="text-align:right">Rate</th><th>Periods</th><th style="text-align:right">Gross</th><th>Discount</th><th>Value</th><th style="text-align:right">Net Amount</th></tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                `);
                dialog.fields_dict.billing_preview.$wrapper.find('tr[data-key]').each(function() {
                    let $row = $(this);
                    let key = $row.attr('data-key');
                    $row.find('.line-qty').on('change', function() {
                        let val = parseInt($(this).val(), 10);
                        if (!val || val < 1) val = 1;
                        dialog.custom_quantities[key] = val;
                        refresh_billing_preview(dialog);
                    });
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
