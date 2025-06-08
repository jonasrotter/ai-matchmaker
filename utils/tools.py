import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table
from dotenv import load_dotenv
from openai import OpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)
from azure.core.credentials import AzureKeyCredential
import dotenv

dotenv.load_dotenv()

AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
INDEX_NAME = "prod-index"
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"

client = SearchClient(AISEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AISEARCH_KEY))
oai = OpenAI()

def get_products(query):
    query_vector = VectorizedQuery(vector=get_embedding(query), k_nearest_neighbors=3, fields="text_vector")

    results = client.search(
        query,
        top=2,  
        vector_queries=[query_vector],
        select=["productDisplayName", "subCategory", "baseColour","gender"],
        query_type=QueryType.SEMANTIC,
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
    )

    semantic_answers = results.get_answers()
    return semantic_answers[0].text
    

# Utility function to retrieve qna data from AI Search
def get_faq(query):
    query_vector = VectorizedQuery(vector=get_embedding(query), k_nearest_neighbors=3, fields="text_vector")

    results = client.search(
        query,
        top=2,  
        vector_queries=[query_vector],
        select=["Category", "Question", "Answer"],
        query_type=QueryType.SEMANTIC,
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
    )

    semantic_answers = results.get_answers()
    return semantic_answers[0].text

# Utility function to retrieve POS data from PostgreSQL
def get_pos(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records', lines=True)
    except Exception as e:
        return f"Error executing pos query: {e}"

# Utility function to retrieve CRM context data from PostgreSQL
def get_crm(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records', lines=True)
    except Exception as e:
        return f"Error executing pos query: {e}"

# Utility function to retrieve ERP data from PostgreSQL
def get_erp(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records', lines=True)
    except Exception as e:
        return f"Error executing pos query: {e}"

def get_pg_schema(table_name: str, engine) -> str:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    schema_lines = [f"- {col.name} ({col.type})" for col in table.columns]
    return f"Table: {table_name}\nColumns:\n" + "\n".join(schema_lines)

def get_embedding(text):
    get_embeddings_response = oai.embeddings.create(model=EMBEDDING_MODEL, input=text, dimensions=3072)
    return get_embeddings_response.data[0].embedding