import os
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import dotenv
from openai import OpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

dotenv.load_dotenv()

AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
INDEX_NAME = "products-index"
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"

client = SearchClient(AISEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AISEARCH_KEY))
oai = OpenAI()

def get_embedding(text):
    get_embeddings_response = oai.embeddings.create(model=EMBEDDING_MODEL, input=text, dimensions=3072)
    return get_embeddings_response.data[0].embedding


def main():
    user_question = "Do you have blue pants for man?"
    user_question_vector = get_embedding(user_question)

    results = client.search(
        user_question,
        top=5, 
        vector_queries=[
                VectorizedQuery(vector=user_question_vector, k_nearest_neighbors=3, fields="text_vector")],
    )

    print("Test")

    for result in results: 
        print(result)

if __name__ == '__main__':
    main()