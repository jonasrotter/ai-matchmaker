import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

connection_params = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT', '5432'),
    "dbname": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD')
}


def get_pg_schema(connection_params: dict, table_name: str) -> str:
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not rows:
        return f"No schema found for table '{table_name}'"
    
    schema_lines = [f"- {col} ({dtype})" for col, dtype in rows]
    return f"Table: {table_name}\nColumns:\n" + "\n".join(schema_lines)


def get_pos(connection_params: dict, query):
    """Retrieve all rows from the pos table in the retailNext database on the psqlmatchmaker server."""
    try:
        conn = psycopg2.connect(**connection_params)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"

def main():
    pos_schema = get_pg_schema(connection_params, "pos")
    print(pos_schema)
    results = get_pos(connection_params, f"""
        SELECT *
        FROM pos
    """)
    print(results.head(5))
    print("Success")


if __name__ == '__main__':
    main()