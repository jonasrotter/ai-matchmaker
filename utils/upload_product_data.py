from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchClient, SearchIndexingBufferedSender  

from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
from openai import OpenAI
import pandas as pd

# Load environment variables
load_dotenv()
client = OpenAI()

GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
index_name = "products-index"


def upload_data():
    # Convert the 'id' and 'vector_id' columns to string so one of them can serve as our key field
    df = pd.read_csv("data/sample_styles_with_embeddings.csv")
    df["id"] = df["id"].astype(str)

    # Convert the DataFrame to a list of dictionaries
    documents = df.to_dict(orient="records")

    # Create a SearchIndexingBufferedSender
    batch_client = SearchIndexingBufferedSender(
        AISEARCH_ENDPOINT, index_name, AzureKeyCredential(AISEARCH_KEY)
    )

    try:
        # Add upload actions for all documents in a single call
        batch_client.upload_documents(documents=documents)

        # Manually flush to send any remaining documents in the buffer
        batch_client.flush()
    except HttpResponseError as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up resources
        batch_client.close()

    print(f"Uploaded {len(documents)} documents in total")

if __name__ == '__main__':
    upload_data()
    print("Success!")