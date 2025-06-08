import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table
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
def get_pos(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"

# Utility function to retrieve CRM context data from PostgreSQL
def get_crm(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"

# Utility function to retrieve ERP data from PostgreSQL
def get_erp(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"

def get_pg_schema(table_name: str, engine) -> str:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    schema_lines = [f"- {col.name} ({col.type})" for col in table.columns]
    return f"Table: {table_name}\nColumns:\n" + "\n".join(schema_lines)