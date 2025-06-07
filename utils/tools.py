import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


def get_products(keyword):
    path = "data/sample_styles_with_embeddings.csv"
    df = pd.read_csv(path, on_bad_lines='skip')
    return df.head(5)

# Utility function to retrieve qna data from AI Search
def get_faq(query):
    path = "data/qna.csv"
    df = pd.read_csv(path, on_bad_lines='skip')
    return df.head(5)

# Utility function to retrieve POS data from PostgreSQL
def get_pos(query):
    """Retrieve all rows from the pos table in the retailNext database on the psqlmatchmaker server."""
    load_dotenv()
    try:
        conn = psycopg2.connect(
            host="psqlmatchmaker",
            port=os.getenv('DB_PORT', '5432'),
            database="retailNext",
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"

# Utility function to retrieve CRM context data from PostgreSQL
def get_crm(customer_name):
    path = "data/crm.csv"
    df = pd.read_csv(path, on_bad_lines='skip')
    return df.head(5)

# Utility function to retrieve ERP data from PostgreSQL
def get_erp(product_id, store=None):
    path = "data/erp.csv"
    df = pd.read_csv(path, on_bad_lines='skip')
    return df.head(5)

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