from utils.tools import get_crm, get_erp, get_pos, get_products, get_faq, get_pg_schema
from utils.tools import call_function 
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
from sqlalchemy import create_engine, MetaData, Table
import streamlit as st

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

# Create a SQLAlchemy engine using environment variables
engine = create_engine(
    f"postgresql://{connection_params['user']}:{connection_params['password']}@"
    f"{connection_params['host']}:{connection_params['port']}/{connection_params['dbname']}"
)

# Get the schema for the pos table
pos_schema = get_pg_schema("pos", engine=engine)
erp_schema = get_pg_schema("erp", engine=engine)
crm_schema = get_pg_schema("crm", engine=engine)
#products_schema = get_pg_schema("products", engine)

# OpenAI Client Setup
GPT_MODEL = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_COST_PER_1K_TOKENS = 0.00013
#with open("prompts/systemprompt.md", "r", encoding="utf-8") as f:
#    SYSTEM_PROMPT = f.read()
SYSTEM_PROMPT="Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
client = OpenAI()



#Utility function to retrieve data with functions from PostgreSQL database or AI Search
tools = [{
    "type": "function",
    "function": {
        "name": "get_crm",
        "description": "Get information about the customer like loyalty_status, preferred_colors, preferred_sizes",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {crm_schema}
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
        "name": "get_erp",
        "description": "Retrieve stock and restock information for a product from the ERP system",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {erp_schema}
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
        "description": "Search for relevant products based on the questions asked by the user that is stored within the vector database using a semantic query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The natural language query to search the vector database."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return.",
                    "default": 3
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_faq",
        "description": "Search for relevant FAQs about Discounts, Return Policy, Loyalty Programs and General Questions about the Store, based on the questions asked by the user that is stored within the vector database using a semantic query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The natural language query to search the vector database."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return.",
                    "default": 3
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}
]



def store_assistant_agent(user_query: str):
    print(f"User query: {user_query}")
    #messages = []
    #messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # Step #1: Prompt with content that may result in function call. In this case the model can identify the information requested by the user is potentially available in the database schema passed to the model in Tools description. 
    #messages.append({"role": "user", "content": user_query})
    st.session_state.messages.append({"role": "user", "content": user_query})
    print(f"Messages: {st.session_state.messages}")
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    print(f"Assistant message: {assistant_message}")
    #messages.append({"role": "assistant", "content": assistant_message.content})


    # Step 2: determine if the response from the model includes a tool call.   
    tool_calls = assistant_message.tool_calls
    
    print(f"Assistant message: {tool_calls}")
    print(f"Tool calls: {tool_calls}")
    if tool_calls:
        # If true the model will return the name of the tool / function to call and the argument(s)  
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        tool_query_string = json.loads(tool_calls[0].function.arguments)['query']

        st.session_state.messages.append({"role": "assistant", "tool_calls": tool_calls, "content":tool_function_name})
        
        print(f"Tool function name: {tool_function_name}")
        print(f"Tool query string: {tool_query_string}")
        print(f"Tool call ID: {tool_call_id}")
        results = call_function(tool_function_name, tool_query_string, engine)
        
        st.session_state.messages.append({
            "role":"tool", 
            "tool_call_id":tool_call_id,
            "content": results,
            "tool_query_string": tool_query_string,
            "name": tool_function_name
        })


        model_response_with_function_call = client.chat.completions.create(
            model=GPT_MODEL,
            messages=st.session_state.messages,
            stream=False
        ) 
        final_content = model_response_with_function_call.choices[0].message.content
        
        # Handle response
        st.session_state.messages.append({"role": "assistant", "content": final_content})

        print(f"Messages: {st.session_state.messages}")
        return final_content

    else: 
        # Model did not identify a function to call, result can be returned to the user 
        print(assistant_message.content) 
        

if __name__ == "__main__":    
    print("Starting store assistant agent...")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
          break
        store_assistant_agent(user_input)
    print("Store assistant agent completed.")