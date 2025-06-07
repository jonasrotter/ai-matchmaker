
import streamlit as st
import pandas as pd
from PIL import Image

# Load Q&A data
@st.cache_data
def load_qa():
    df = pd.read_csv("retail_store_employee_qna_reordered.csv")
    return df

df = load_qa()

st.title("🛍️ Retail Store Employee Assistant")

# Image upload
uploaded_file = st.file_uploader("Upload a customer image (optional):", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# User input
query = st.text_input("Ask a customer question:")

if query:
    # Simple search (case-insensitive substring match)
    results = df[df["Question"].str.lower().str.contains(query.lower())]

    if not results.empty:
        for _, row in results.iterrows():
            st.markdown(f"**Q:** {row['Question']}")
            st.markdown(f"**A:** {row['Answer']}")
            st.markdown("---")
    else:
        st.info("Sorry, I couldn't find an answer to that question.")
