from utils.functions import get_crm, get_erp, get_pos, get_products, get_qna
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)
import pandas as pd
import numpy as np
import json
import ast
import tiktoken
import concurrent
from openai import OpenAI
from tqdm import tqdm
from tenacity import retry, wait_random_exponential, stop_after_attempt
from IPython.display import Image, display, HTML
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# OpenAI Client Setup
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_COST_PER_1K_TOKENS = 0.00013
client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_crm",
        "description": "Get information about the customer like preferenced email, loyalty_status, preferred_colors, preferred_sizes",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Name of the customer to retrieve information for."
                    }
                },
                "required": ["customer_name"],
                "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_erp",
        "description": "Retrieve stock and restock information for a product from the ERP system",
        "parameters": {
            "type": "object",
            "properties": {
            "product_id": {
                "type": "integer",
                "description": "The ID of the product to check"
            },
            "store": {
                "type": "string",
                "description": "The store location name"
            }
            },
            "required": ["product_id"]
        }
    }
},
  {
    "type": "function",
    "function": {
        "name": "get_pos",
        "description": "Retrieve sales summary from POS system",
        "parameters": {
            "type": "object",
            "properties": {
            "product_id": {
                "type": "integer",
                "description": "The ID of the product sold"
            }
            },
            "required": ["product_id"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_products",
        "description": "Search for product names in the product database",
        "parameters": {
            "type": "object",
            "properties": {
            "keyword": {
                "type": "string",
                "description": "Keyword to search for in product names"
            }
            },
            "required": ["keyword"]
        }
    }
},
  {
    "type": "function",
    "function": {
        "name": "get_faq",
        "description": "Retrieve an answer from the employee Q&A database",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The question or phrase to search the Q&A for"
            }
            },
            "required": ["query"]
        }
    }
}
]

def main ():
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": "Is there Wifi in the store?"})

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)
    print(assistant_message) 

if __name__ == "__main__":
    main()