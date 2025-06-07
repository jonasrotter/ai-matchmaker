import pandas as pd
#Utility function to retrieve product data from AI Search
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


def generate_embeddings(text, client, embedding_model):
    # Generate embeddings for the provided text using the specified model
    embeddings_response = client.embeddings.create(model=embedding_model, input=text)
    # Extract the embedding data from the response
    embedding = embeddings_response.data[0].embedding
    return embedding