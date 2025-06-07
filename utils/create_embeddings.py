from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender  
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
load_dotenv()
client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-large"


def get_embeddings(input: list):
    response = client.embeddings.create(
        input=input,
        model=EMBEDDING_MODEL
    ).data
    print("Embeddings created successfully.")
    return [data.embedding for data in response]
    

# Function to generate embeddings for a given column in a DataFrame
def generate_embeddings(df, column_name):
    # Initialize an empty list to store embeddings
    descriptions = df[column_name].astype(str).tolist()
    embeddings = get_embeddings(descriptions)

    # Add the embeddings as a new column to the DataFrame
    df['embeddings'] = embeddings

if __name__ == '__main__':
    df = pd.read_csv("data/products.csv")
    generate_embeddings(df, "productDisplayName")
    df.to_csv('data/products_with_embeddings.csv', index=False)
    print("Success!")