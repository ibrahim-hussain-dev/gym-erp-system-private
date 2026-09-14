import io

def patch(path, replacements):
    with io.open(path, encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        if content.count(old) != 1:
            print(f"WARNING: anchor not found or not unique in {path}: {old[:80]!r}")
            continue
        content = content.replace(old, new, 1)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {path}")


# --- gym_fitness_log.py: fix height_cm -> height_feet sync bug ---
patch("apps/gym_management/gym_management/gym_erp_system/doctype/gym_fitness_log/gym_fitness_log.py", [
    (
"""import frappe
from frappe.model.document import Document""",
"""import frappe
from frappe.model.document import Document
from frappe.utils import flt"""
    ),
    (
"""        if self.height_cm:
            updates["height_cm"] = self.height_cm""",
"""        if self.height_cm:
            updates["height_feet"] = flt(self.height_cm) / 30.48"""
    ),
])

# --- sell_membership.js: plans label+description, auto-renew default, billing table full width ---
patch("apps/gym_management/gym_management/gym_erp_system/page/sell_membership/sell_membership.js", [
    (
"""                {
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
                },""",
"""                {
                    fieldname: 'plans',
                    fieldtype: 'MultiSelectPills',
                    label: 'Plans (select Registration + Membership + any add-ons together)',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2',
                    get_data: function(txt) {
                        return frappe.db.get_list('Gym Plan', {
                            filters: { disabled: 0 },
                            fields: ['name', 'plan_name', 'plan_group', 'duration_value', 'duration_unit', 'one_time_charge'],
                            limit: 20
                        }).then(data => data.map(d => {
                            let duration_text = d.one_time_charge
                                ? 'One-Time Charge'
                                : `${d.duration_value} ${d.duration_unit}`;
                            return {
                                value: d.name,
                                label: d.plan_name,
                                description: `${d.plan_group} \\u00b7 ${duration_text}`
                            };
                        }));
                    },
                    onchange: () => refresh_billing_preview(dialog)
                },"""
    ),
    (
"""                {
                    fieldname: 'auto_renew',
                    fieldtype: 'Check',
                    label: 'Auto-Renew this membership when it expires',
                    default: 0,
                    description: 'When the membership expires, a new invoice will be generated automatically and the membership will continue.',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },""",
"""                {
                    fieldname: 'auto_renew',
                    fieldtype: 'Check',
                    label: 'Auto-Renew this membership when it expires',
                    default: 1,
                    description: 'When the membership expires, a new invoice will be generated automatically and the membership will continue.',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },"""
    ),
    (
"""                {
                    fieldname: 'col_break_overall_discount',
                    fieldtype: 'Column Break',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },""",
"""                {
                    fieldname: 'col_break_overall_discount',
                    fieldtype: 'Section Break',
                    depends_on: 'eval:!doc.is_new_member || doc.step==2'
                },"""
    ),
])

print("ALL DONE")
