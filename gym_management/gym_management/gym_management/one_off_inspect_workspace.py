import frappe
import json

def run():
    rows = frappe.db.sql("""
        select name, title, module, public, icon, parent_page, sequence_id, label, content
        from `tabWorkspace`
        where module like %s or title like %s or name like %s
    """, ('%Gym%', '%Gym%', '%Gym%'), as_dict=True)

    if not rows:
        print("No Workspace record found matching 'Gym'.")
        return

    for r in rows:
        print("-----")
        print("name:", repr(r.name))
        print("title:", repr(r.title))
        print("module:", repr(r.module))
        print("public:", repr(r.public))
        print("icon:", repr(r.icon))
        print("parent_page:", repr(r.parent_page))
        print("sequence_id:", repr(r.sequence_id))
        print("label:", repr(r.label))
        content_len = len(r.content) if r.content else 0
        print("content length:", content_len)
