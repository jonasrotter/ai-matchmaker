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
import base64

dotenv.load_dotenv()

AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"


# Retrieve Product data from AI Search
def get_products(query):
    query_vector = VectorizedQuery(vector=get_embedding(query), k_nearest_neighbors=3, fields="text_vector")
    search_client = SearchClient(AISEARCH_ENDPOINT, "prod-index", AzureKeyCredential(AISEARCH_KEY))
    results = search_client.search(
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
    

# Retrieve FAQ data from AI Search
def get_faq(query):
    query_vector = VectorizedQuery(vector=get_embedding(query), k_nearest_neighbors=3, fields="text_vector")
    search_client = SearchClient(AISEARCH_ENDPOINT, "qna-index", AzureKeyCredential(AISEARCH_KEY))
    results = search_client.search(
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

# Retrieve POS data from PostgreSQL
def get_pos(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records', lines=True)
    except Exception as e:
        return f"Error executing pos query: {e}"

# Retrieve CRM data from PostgreSQL
def get_crm(query, engine):
    try:
        df = pd.read_sql_query(query, engine)
        return df.to_json(orient='records', lines=True)
    except Exception as e:
        return f"Error executing pos query: {e}"

# Retrieve ERP data from PostgreSQL
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

def get_embedding(text, client=OpenAI()):
    get_embeddings_response = client.embeddings.create(model=EMBEDDING_MODEL, input=text, dimensions=3072)
    return get_embeddings_response.data[0].embedding

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read())
        return encoded_image.decode('utf-8')
    
def analyze_image(image_base64, client=OpenAI()):
    # Product subcateorie
    subcategories = pd.read_csv("data/products.csv")['articleType'].unique()
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"""Given an image of an item of clothing, analyze the item and generate a JSON output with the following fields: "items", "category", and "gender".
                           Use your understanding of fashion trends, styles, and gender preferences to provide accurate and relevant suggestions for how to complete the outfit.
                           The items field should be a list of items that would go well with the item in the picture. Each item should represent a title of an item of clothing that contains the style, color, and gender of the item.
                           The category needs to be chosen between the types in this list: {subcategories}.
                           You have to choose between the genders in this list: [Men, Women, Boys, Girls, Unisex]
                           Do not include the description of the item in the picture. Do not include the ```json ``` tag in the output.

                           Example Input: An image representing a black leather jacket.

                           Example Output: {{"items": ["Fitted White Women's T-shirt", "White Canvas Sneakers", "Women's Black Skinny Jeans"], "category": "Jackets", "gender": "Women"}}
                           """,
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                },
                }
            ],
            }
        ]
    )
    # Extract relevant features from the response
    features = response.choices[0].message.content
    return features