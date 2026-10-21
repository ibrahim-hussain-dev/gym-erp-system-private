import frappe

def run():
    meta = frappe.get_meta("Workspace")
    fieldnames = [f.fieldname for f in meta.fields]
    print("WORKSPACE DOCTYPE FIELDS:", fieldnames)

    ws_list = frappe.get_all("Workspace", filters={"title": ["like", "%Gym%"]}, fields=["name", "title", "public"])
    print("GYM WORKSPACES FOUND:", ws_list)

    for w in ws_list:
        doc = frappe.get_doc("Workspace", w.name)
        print("----", w.name, "----")
        print("public:", doc.get("public"))
        print("for_user:", doc.get("for_user"))
        if hasattr(doc, "roles"):
            print("roles child table:", [r.as_dict() for r in doc.roles])
        else:
            print("no 'roles' field on this doc")
        content = doc.get("content") or ""
        print("content length:", len(content))

    all_roles = frappe.get_all("Role", filters={"name": ["like", "Gym%"]}, pluck="name")
    print("GYM ROLES:", all_roles)
