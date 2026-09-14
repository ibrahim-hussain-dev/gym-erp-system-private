frappe.pages['record-expense'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Record Expense',
        single_column: true
    });
    page.set_primary_action('New Expense', () => open_expense_dialog(), 'add');
    open_expense_dialog();

    function open_expense_dialog() {
        let dialog = new frappe.ui.Dialog({
            title: 'Record Expense',
            fields: [
                {
                    fieldname: 'expense_date',
                    fieldtype: 'Date',
                    label: 'Expense Date',
                    default: frappe.datetime.get_today(),
                    reqd: 1
                },
                {
                    fieldname: 'category',
                    fieldtype: 'Select',
                    label: 'Category',
                    options: 'Salary\nUtilities\nMaintenance\nEquipment Purchase\nPetty Cash\nRent\nMarketing\nOther',
                    reqd: 1
                },
                {
                    fieldname: 'col_break_1',
                    fieldtype: 'Column Break'
                },
                {
                    fieldname: 'amount',
                    fieldtype: 'Currency',
                    label: 'Amount',
                    reqd: 1
                },
                {
                    fieldname: 'payment_method',
                    fieldtype: 'Select',
                    label: 'Payment Method',
                    options: 'Cash\nBank',
                    default: 'Cash',
                    reqd: 1
                },
                {
                    fieldname: 'section_break_1',
                    fieldtype: 'Section Break'
                },
                {
                    fieldname: 'paid_to',
                    fieldtype: 'Data',
                    label: 'Paid To (Employee / Vendor Name)'
                },
                {
                    fieldname: 'receipt',
                    fieldtype: 'Attach',
                    label: 'Receipt / Bill'
                },
                {
                    fieldname: 'description',
                    fieldtype: 'Small Text',
                    label: 'Description / Notes'
                }
            ],
            primary_action_label: 'Record Expense',
            primary_action: (values) => {
                frappe.call({
                    method: 'gym_management.gym_erp_system.api.record_expense',
                    args: {
                        expense_date: values.expense_date,
                        category: values.category,
                        amount: values.amount,
                        payment_method: values.payment_method,
                        paid_to: values.paid_to,
                        description: values.description,
                        receipt: values.receipt
                    },
                    freeze: true,
                    freeze_message: 'Recording expense...',
                    callback: function(r) {
                        if (r.message) {
                            dialog.hide();
                            frappe.msgprint({
                                title: 'Expense Recorded',
                                indicator: 'green',
                                message: `Expense <b>${r.message.name}</b> recorded. Journal Entry: <b>${r.message.journal_entry}</b>`
                            });
                            frappe.set_route('Form', 'Gym Expense', r.message.name);
                        }
                    }
                });
            }
        });
        dialog.show();
    }
};
