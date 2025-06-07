from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)
from dotenv import load_dotenv
import os
from openai import OpenAI
import pandas as pd
import base64
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from utils.tools import get_products

# Load environment variables
load_dotenv()

# OpenAI Client Setup
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
client = OpenAI()

# Azure AI Search Client Setup
AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
index_name = "product-index"
search_client = SearchClient(AISEARCH_ENDPOINT, index_name, AzureKeyCredential(AISEARCH_KEY))  

# Product subcateorie
df = pd.read_csv("data/sample_styles.csv")
unique_subcategories = df['articleType'].unique()

# Define available functions for model to call
tool_definitions = [
    {
        "name": "get_products",
        "description": "Retrieve a list of products matching a search query from the local dataset.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term to filter products by label or attributes."}
            },
            "required": ["query"]
        }
    }
]

@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
def chat_with_tools(user_query: str) -> str:
    # Initial request allowing function calls
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "user", "content": user_query}
        ],
        functions=tool_definitions,
        function_call="auto"
    )
    message = response.choices[0].message

    tool_call = message.function_call
    function_name = tool_call.name

    # If model requests a function call, execute it
    if function_name == "get_products":
        function_args = json.loads(tool_call.arguments)
        print("Function call detected")


def main():
    answer = chat_with_tools("I want to find some products related to 'summer dresses'. Can you help me with that?")
    print("Assistant:", answer)


if __name__ == '__main__':
    main()