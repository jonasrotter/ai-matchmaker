# AI Matchmaker

## Overview
This project is an AI-powered outfit recommendation assistant that combines GPT-4o with Retrieval-Augmented Generation (RAG). It uses a dataset of clothing styles, precomputed embeddings, and sample images to generate personalized outfit suggestions based on natural language queries.

## File Structure
- `data/` : Sample data for Customer (CRM), Styles (Product), Transactions (POS), Stock (ERP), QnA (FAQ) 
- `prompts/` : Agent’s system prompt and examples
- `utils/` : Supporting Functions
- `app.py`                   : Streamlit UI for interactive chat assistant
- `model_tools.py`           : Console-based agent backend with function/tool calls
- `How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb` : Foundations notebook demo
- `StoreAssistant_RetailNext.ipynb`  : Core functionality notebook demo
- `requirements.txt`        : Python dependencies
- `README.md`               : Project documentation

## Setup and Installation
1. Create a Python virtual environment (if not already present):
   ```powershell
   python -m venv aimatchenv
   ```
2. Activate the virtual environment:
   ```powershell
   .\aimatchenv\Scripts\Activate
   ```
3. Install required packages:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the project root (this file is ignored by git) and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage
You can explore and run this project in three ways:

1. Foundations Notebook
   - File: `How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb`
   - Launch with:
     ```powershell
     jupyter notebook How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb
     ```
   - Use this notebook to understand the underlying GPT-4o + RAG integration.

2. Core Functionality Notebook
   - File: `StoreAssistant_RetailNext.ipynb`
   - Launch with:
     ```powershell
     jupyter notebook StoreAssistant_RetailNext.ipynb
     ```
   - Use this notebook to explore the agent architecture and utility tools for Product, POS, ERP, CRM, and FAQ queries.

4. Store Agent Backend
   - Script: `model_tools.py`
   - Run with Streamlit:
     ```powershell
     python model_tools.py
     ```
   - Use this python script to test the agent tools capabilities via the command line.

3. User-Friendly UI
   - Script: `app.py`
   - Run with Streamlit:
     ```powershell
     streamlit run app.py
     ```
   - Launches an interactive chat interface where you can ask about store data, upload images, and receive AI-powered responses.