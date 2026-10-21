import frappe


def run():
    search_term = "impact_logo_512"
    rows = frappe.db.sql(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND data_type IN ('varchar', 'text', 'longtext', 'mediumtext', 'char')
        ORDER BY table_name, column_name
        """,
        as_dict=True,
    )
    print(f"Scanning {len(rows)} text-like columns across the database for '{search_term}'...")
    print()

    hits = []
    for row in rows:
        table = row["table_name"]
        column = row["column_name"]
        try:
            found = frappe.db.sql(
                f"""
                SELECT `name`, `{column}`
                FROM `{table}`
                WHERE `{column}` LIKE %s
                LIMIT 5
                """,
                (f"%{search_term}%",),
                as_dict=True,
            )
        except Exception as e:
            continue
        if found:
            hits.append((table, column, found))

    if not hits:
        print(f"No rows found containing '{search_term}' anywhere in the database.")
        return

    print(f"Found {len(hits)} column(s) with matches:")
    print()
    for table, column, found in hits:
        print(f"=== table: {table}, column: {column} ===")
        for r in found:
            print(f"  name={r['name']!r}  value={r[column]!r}")
        print()
