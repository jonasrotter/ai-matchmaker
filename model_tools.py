from utils.tools import get_crm, get_erp, get_pos, get_products, get_faq, get_pg_schema 
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

# PSQL Connection String
connection_params = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT', '5432'),
    "dbname": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD')
}
pos_schema = get_pg_schema(connection_params, "pos")

# OpenAI Client Setup
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_COST_PER_1K_TOKENS = 0.00013
client = OpenAI()



#Utility function to retrieve product data from AI Search
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
        "description": "Use this function to answer questions about sales transactions. Input should be a fully formed SQL query. The query should use the pos table in the retailNext database.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {pos_schema}
                                The query should be returned in plain text, not in JSON.
                                """, 
            }
            },
            "required": ["query"]
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

def model_tools(user_prompt: str):
    # "Is there Wifi in the store?"
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

        # Handle function call (if any)
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            arguments = eval(tool_call.function.arguments)

            # Dynamically import function from utils.tools
            from utils import tools
            func = getattr(tools, func_name)

            result = func(**arguments)


def main ():
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    a="Is there Wifi in the store?"
    b= "What is the stock for product 123 in store A?"
    c= "What is the sales summary for product 456?"
    d= "What are the customer preferences for John Doe?"

    # Step #1: Prompt with content that may result in function call. In this case the model can identify the information requested by the user is potentially available in the database schema passed to the model in Tools description. 
    messages.append({"role": "user", "content": c})

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)
    print(assistant_message)

    # Step 2: determine if the response from the model includes a tool call.   
    tool_calls = assistant_message.tool_calls
    if tool_calls:
        # If true the model will return the name of the tool / function to call and the argument(s)  
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        
        tool_function_name

        # Step 3: Call the function and retrieve results. Append the results to the messages list.      
        if tool_function_name == 'get_pos':
            results = get_pos()  
            
            messages.append({
                "role":"tool", 
                "tool_call_id":tool_call_id, 
                "name": tool_function_name, 
                "content":results
            })
            
            # Step 4: Invoke the chat completions API with the function response appended to the messages list
            # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print(model_response_with_function_call.choices[0].message.content)
        else: 
            print(f"Error: function {tool_function_name} does not exist")
    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(assistant_message.content) 

if __name__ == "__main__":
    main()