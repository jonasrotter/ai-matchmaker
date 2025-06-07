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
INDEX_NAME = "qna-index"


def upload_data():
    # Convert the 'id' and 'vector_id' columns to string so one of them can serve as our key field
    df = pd.read_csv("data/qna_with_embeddings.csv")
    df["ID"] = df["ID"].astype(str)

    # Convert the DataFrame to a list of dictionaries
    documents = df.to_dict(orient="records")


    # Use buffered sender to handle large batches
    #with SearchIndexingBufferedSender(AISEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AISEARCH_KEY)) as client:
    client = SearchClient(AISEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AISEARCH_KEY)) 
    client.upload_documents(documents=documents)
        # Flush any remaining buffered documents



    print(f"Uploaded {len(documents)} documents in total")

if __name__ == '__main__':
    upload_data()
    print("Success!")