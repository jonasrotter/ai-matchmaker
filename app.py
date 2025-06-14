import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv 
from PIL import Image
import json
from utils.tools import get_products
from dotenv import load_dotenv
import os
import base64
from utils.tools import analyze_image
from model_tools import store_assistant_agent

# Load environment variables
load_dotenv()
unique_subcategories = pd.read_csv("data/products.csv")['subCategory'].unique()

# OpenAI Client Setup
GPT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
# OpenAI Client
client = OpenAI()

#with open("prompts/systemprompt_simple.md", "r", encoding="utf-8") as f:
with open("prompts/systemprompt_advanced.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
#SYSTEM_PROMPT="Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

st.title("🛍️ RetailNext Store Assistant")

# User input
user_input = st.chat_input("Ask something about the store, customer, or product...")

# Image upload
uploaded_file = st.file_uploader("Upload an item image", type=["jpg", "jpeg", "png"])

if user_input:
    # Display user message
    item_descs = ""
    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded image", use_column_width=True)
        # Read and encode to base64
        img_bytes = uploaded_file.read()
        encoded = base64.b64encode(img_bytes).decode("utf-8")
        # Analyze via model
        analysis = analyze_image(encoded)
        image_analysis = json.loads(analysis)
        
        # Extract the relevant features from the analysis
        item_descs = image_analysis['items'][0]
        # Show analysis results
        st.subheader("Image Analysis")

    user_input = user_input + item_descs
    #st.session_state.messages.append({"role": "user", "content": user_input})
    # Send to OpenAI with tool calling
    response = store_assistant_agent(user_input)


# After processing input, render the full chat history
for m in st.session_state.messages:
    if m["role"] == "tool":
        st.chat_message(m["role"]).markdown(m["tool_query_string"])
    elif m["role"] != "system":
        st.chat_message(m["role"]).markdown(m["content"])
