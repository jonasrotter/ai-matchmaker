import pandas as pd
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
def get_pos():
    path = "data/pos.csv"
    df = pd.read_csv(path, on_bad_lines='skip')
    return df.head(5)

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

