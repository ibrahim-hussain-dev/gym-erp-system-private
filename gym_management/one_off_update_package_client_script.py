import frappe

def run():
    script = """
function recalc(frm) {
    let mode = frm.doc.pricing_mode;
    let rows = frm.doc.items || [];

    if (mode === 'Manual Per-Service Price') {
        let total = rows.reduce((sum, r) => sum + flt(r.price), 0);
        frm.set_value('overall_price', total);
    } else if (rows.length) {
        let overall = flt(frm.doc.overall_price);
        if (mode === 'One Total Price - Equal Split') {
            let each = overall / rows.length;
            rows.forEach(r => { r.price = each; });
        } else if (mode === 'One Total Price - Proportional Split') {
            let total_weight = rows.reduce((sum, r) => sum + flt(r.plan_price), 0) || 1;
            rows.forEach(r => {
                let weight = flt(r.plan_price) / total_weight;
                r.price = overall * weight;
            });
        }
        frm.refresh_field('items');
    }
}

frappe.ui.form.on('Gym Package', {
    pricing_mode: function(frm) {
        recalc(frm);
    },
    overall_price: function(frm) {
        recalc(frm);
    },
    items_add: function(frm) {
        recalc(frm);
    },
    items_remove: function(frm) {
        recalc(frm);
    }
});

frappe.ui.form.on('Gym Package Item', {
    gym_plan: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.gym_plan) return;
        frappe.db.get_value('Gym Plan', row.gym_plan, 'monthly_fee', (r) => {
            row.plan_price = r.monthly_fee || 0;
            if (frm.doc.pricing_mode === 'Manual Per-Service Price') {
                row.price = row.plan_price;
            }
            frm.refresh_field('items');
            recalc(frm);
        });
    },
    price: function(frm) {
        recalc(frm);
    }
});
"""
    if frappe.db.exists("Client Script", "Gym Package-Form-AutoPrice"):
        frappe.db.set_value("Client Script", "Gym Package-Form-AutoPrice", "script", script)
        print("Updated existing Client Script: Gym Package-Form-AutoPrice")
    else:
        doc = frappe.get_doc({
            "doctype": "Client Script",
            "name": "Gym Package-Form-AutoPrice",
            "dt": "Gym Package",
            "view": "Form",
            "enabled": 1,
            "script": script,
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        print("Created Client Script: Gym Package-Form-AutoPrice")
    frappe.db.commit()
