import frappe

def run():
    doc = frappe.get_doc("Workspace", "Gym Operations")

    print("=" * 60)
    print(f"LINKS TABLE: {len(doc.links)} rows")
    print("=" * 60)
    for i, row in enumerate(doc.links):
        print(f"idx={row.idx} | {row.as_dict()}")

    print()
    print("=" * 60)
    print(f"QUICK_LISTS TABLE: {len(doc.quick_lists)} rows")
    print("=" * 60)
    for row in doc.quick_lists:
        print(f"idx={row.idx} | {row.as_dict()}")

    print()
    print("=" * 60)
    print(f"CUSTOM_BLOCKS TABLE: {len(doc.custom_blocks)} rows")
    print("=" * 60)
    for row in doc.custom_blocks:
        print(f"idx={row.idx} | {row.as_dict()}")

    print()
    print("=" * 60)
    print("CONTENT FIELD (raw, first 3000 chars) - dead links might be embedded here")
    print("=" * 60)
    print((doc.content or "")[:3000])
