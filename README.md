# AI Matchmaker

## Overview
This project is an AI-powered outfit recommendation assistant that combines GPT-4o with Retrieval-Augmented Generation (RAG). It uses a dataset of clothing styles, precomputed embeddings, and sample images to generate personalized outfit suggestions based on natural language queries.

## File Structure
- `data/`
  - `sample_styles.csv`            : Raw style data (labels, attributes)
  - `sample_styles_with_embeddings.csv` : Styles with precomputed vector embeddings for similarity search
  - `sample_images/`               : Example product images used for reference
- `How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb` : Jupyter notebook demonstrating end-to-end usage
- `requirements.txt`     : List of Python dependencies
- `README.md`            : This documentation file

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
- Launch the Jupyter notebook to run the outfit assistant demo:
  ```powershell
  jupyter notebook How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb
  ```