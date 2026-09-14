import frappe

def run():
    meta = frappe.get_meta("Workspace")
    icon_field = [f for f in meta.fields if f.fieldname == "icon"]
    if icon_field:
        f = icon_field[0]
        print("icon field type:", f.fieldtype, "| options:", f.options)
    else:
        print("No 'icon' field found on Workspace doctype")

    ws = frappe.get_doc("Workspace", "Gym Operations")
    print("Current icon value:", ws.icon)

    # Try setting a fitting emoji icon
    ws.icon = "gym"
    try:
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("Set icon to 'gym' - OK")
    except Exception as e:
        print("Could not set to 'gym':", e)
        ws.icon = "\U0001F4AA"  # 💪 emoji fallback
        try:
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("Set icon to emoji fallback - OK")
        except Exception as e2:
            print("Emoji also failed:", e2)
