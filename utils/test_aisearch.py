import os
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import dotenv
from openai import OpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)

dotenv.load_dotenv()

AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
INDEX_NAME = "prod-index"
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"

client = SearchClient(AISEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AISEARCH_KEY))
oai = OpenAI()

def get_embedding(text):
    get_embeddings_response = oai.embeddings.create(model=EMBEDDING_MODEL, input=text, dimensions=3072)
    return get_embeddings_response.data[0].embedding


def main():
    query = "Do you have blue pants for men?"
    #qqna = "Is there Wifi in the store?"
    query_vector = VectorizedQuery(vector=get_embedding(query), k_nearest_neighbors=3, fields="text_vector")
    print (f"Query: {query}\n")

    #results = client.search(
    #    query,
    #    top=2, 
    #    vector_queries=[query_vector],
    #    select=["productDisplayName", "subCategory", "baseColour","gender"],
    #)

    results = client.search(
        query,
        top=2,  
        vector_queries=[query_vector],
        select=["productDisplayName", "subCategory", "baseColour","gender"],
        query_type=QueryType.SEMANTIC,
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
    )

    semantic_answers = results.get_answers()
    for answer in semantic_answers:
        if answer.highlights:
            print(f"Semantic Answer: {answer.highlights}")
        else:
            print(f"Semantic Answer: {answer.text}")
        print(f"Semantic Answer Score: {answer.score}\n")

    for result in results: 
        print(f"Product Name: {result['productDisplayName']}")  
        print(f"Category: {result['subCategory']}")  
        print(f"Colour: {result['baseColour']}") 
        print(f"Gender: {result['gender']}\n") 

if __name__ == '__main__':
    main()
    print("Completed successfully!")