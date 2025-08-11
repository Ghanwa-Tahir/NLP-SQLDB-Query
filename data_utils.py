import sqlite3
import pandas as pd

def sample_column_values(db_path, table_name, column_name, limit=5):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Get primary keys
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()

        primary_keys = []
        col_type = None
        for col in columns_info:
            if col[5] == 1:  # pk flag
                primary_keys.append(col[1])
            if col[1] == column_name:
                col_type = col[2].upper()

        # 2. Get foreign key mappings
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()

        foreign_key_map = []
        join_clauses = []
        for fk in foreign_keys:
            # fk format: (id, seq, table, from, to, on_update, on_delete, match)
            ref_table = fk[2]       # referenced table
            from_col = fk[3]        # column in current table
            to_col = fk[4]          # column in referenced table (usually PK)
            foreign_key_map.append({
                "from_column": from_col,
                "to_column": to_col,
                "ref_table": ref_table
            })
            join_clauses.append(f"LEFT JOIN {ref_table} ON {table_name}.{from_col} = {ref_table}.{to_col}")

        joins = "\n".join(join_clauses)

        # 3. Add type-based filtering
        where_clause = f"{table_name}.{column_name} IS NOT NULL"
        if col_type:
            if "CHAR" in col_type or "TEXT" in col_type:
                where_clause += f" AND ({table_name}.{column_name} LIKE '%A%' OR {table_name}.{column_name} LIKE '%B%')"
            elif "INT" in col_type or "REAL" in col_type or "NUM" in col_type:
                where_clause += f" AND {table_name}.{column_name} > 50"

        # 4. Final query
        query = f"""
        SELECT {table_name}.{column_name}
        FROM {table_name}
        {joins}
        WHERE {where_clause}
        GROUP BY {table_name}.{column_name}
        ORDER BY COUNT(*) DESC
        LIMIT {limit}
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        print("\n📌 Primary Keys:", primary_keys)
        print("🔗 Foreign Keys:")
        for fk in foreign_key_map:
            print(f"  {table_name}.{fk['from_column']} → {fk['ref_table']}.{fk['to_column']}")

        return df[column_name].dropna().astype(str).tolist()

    except Exception as e:
        print("Error:", e)
        return []
