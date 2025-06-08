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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."}
    ]

st.title("🛍️ Retail Store Assistant")

# User input
user_input = st.chat_input("Ask something about the store, customer, or product...")

# Image upload
uploaded_file = st.file_uploader("Upload an item image", type=["jpg", "jpeg", "png"])

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded image", use_column_width=True)
        # Read and encode to base64
        img_bytes = uploaded_file.read()
        encoded = base64.b64encode(img_bytes).decode("utf-8")
        # Analyze via model
        analysis = analyze_image(encoded, unique_subcategories)
        # Show analysis results
        st.subheader("Image Analysis")

    # Send to OpenAI with tool calling
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto",
    )

    # Handle response
    assistant_msg = response.choices[0].message
    st.session_state.messages.append(assistant_msg)

    # Show assistant reply
    st.chat_message("assistant").markdown(assistant_msg.content or "🔧 (Tool call in progress...)")

    # Handle function call (if any)
    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            arguments = eval(tool_call.function.arguments)

            # Dynamically import function from utils.functions
            from utils import tools
            func = getattr(tools, func_name)

            result = func(**arguments)

            # Show result in chat
            st.chat_message("function").markdown(f"**Function `{func_name}` returned:**\n\n{result}")

            # Add function result as assistant message
            st.session_state.messages.append({
                "role": "function",
                "name": func_name,
                "content": result
            })


