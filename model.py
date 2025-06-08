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
from utils.tools import encode_image_to_base64, analyze_image, get_products

# Load environment variables
load_dotenv()

# OpenAI Client Setup
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_COST_PER_1K_TOKENS = 0.00013
client = OpenAI()

# Azure AI Search Client Setup
AISEARCH_ENDPOINT = os.getenv('AZURE_AISEARCH_ENDPOINT')
AISEARCH_KEY = os.getenv('AZURE_AISEARCH_ADMIN_KEY')
index_name = "prod-index"
search_client = SearchClient(AISEARCH_ENDPOINT, index_name, AzureKeyCredential(AISEARCH_KEY))  


def main():
    # Set the path to the images and select a test image
    image_path = "data/sample_images/"
    test_images = ["2133.jpg", "7143.jpg", "4226.jpg"]

    # Encode the test image to base64
    reference_image = image_path + test_images[0]
    print(reference_image)
    encoded_image = encode_image_to_base64(reference_image)

    # Analyze the image and return the results
    analysis = analyze_image(encoded_image)
    image_analysis = json.loads(analysis)

    # Extract the relevant features from the analysis
    item_descs = image_analysis['items']
    item_category = image_analysis['category']
    item_gender = image_analysis['gender']
    print(item_descs)
    print(item_category)
    print(item_gender)

    results = get_products(item_descs)


    # Display the image and the analysis results
    print(results)



if __name__ == '__main__':
    main()