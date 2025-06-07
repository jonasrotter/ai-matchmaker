import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table
from dotenv import load_dotenv

load_dotenv()

connection_params = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT', '5432'),
    "dbname": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD')
}

# Create a SQLAlchemy engine using environment variables
engine = create_engine(
    f"postgresql://{connection_params['user']}:{connection_params['password']}@"
    f"{connection_params['host']}:{connection_params['port']}/{connection_params['dbname']}"
)


def get_pg_schema(table_name: str) -> str:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    schema_lines = [f"- {col.name} ({col.type})" for col in table.columns]
    return f"Table: {table_name}\nColumns:\n" + "\n".join(schema_lines)


def get_pos(query):
    """Retrieve all rows from the pos table in the retailNext database on the psqlmatchmaker server."""
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        return f"Error executing pos query: {e}"


def main():
    print(engine)
    pos_schema = get_pg_schema("pos")
    print(pos_schema)
    results = get_pos(f"""
        SELECT *
        FROM pos
    """)
    print(results.head(5))
    print("Success")


if __name__ == '__main__':
    main()