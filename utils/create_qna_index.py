from azure.search.documents import SearchClient, SearchIndexingBufferedSender  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()

AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
index_name = "qna-index"


def create_index():
    # Initialize the SearchIndexClient
    client = SearchIndexClient(
        endpoint=AISEARCH_ENDPOINT, credential=AzureKeyCredential(AISEARCH_KEY)
    )

    # Define the fields for the index
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="category", type=SearchFieldDataType.String),
        SearchableField(name="question", type=SearchFieldDataType.String),
        SearchableField(name="answer", type=SearchFieldDataType.String),
        SearchField(
            name="embeddings",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="my-vector-config",
        ),
    ]

    # Configure the vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="my-hnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE,
                ),
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-config",
                algorithm_configuration_name="my-hnsw",
            )
        ],
    )

    # Configure the semantic search configuration
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    keywords_fields=[SemanticField(field_name="category")],
                    content_fields=[SemanticField(field_name="question")],
                ),
            )
        ]
    )

    # Create the search index with the vector search and semantic search configurations
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    # Create or update the index
    result = client.create_or_update_index(index)
    print(f"{result.name} created")

if __name__ == '__main__':
    create_index()
