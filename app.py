import streamlit as st
import pandas as pd
import sqlite3
from vector_utils import semantic_search
from langchain.vectorstores import Chroma  # or your actual vectorstore setup
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

# --- Database Connection ---
conn = sqlite3.connect("Data.db")  # 🔁 Replace with your actual DB path
query_df = "SELECT * FROM users"       # 🔁 Replace with your actual SQL query/table
df = pd.read_sql_query(query_df, conn)

# --- Ensure row index for mapping vectorstore results ---
df.reset_index(inplace=True)
df.rename(columns={"index": "row_idx"}, inplace=True)

# --- Load Vectorstore ---
# Replace this with how you're actually loading the vectorstore
# Example for Chroma:
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

# --- Streamlit UI ---
st.title("Semantic Search on SQL Data")

query = st.text_input("Enter your question")

if query:
    try:
        results_df = semantic_search(query, vectorstore, df)
        st.write("Search Results:")
        st.dataframe(results_df)
    except Exception as e:
        st.error(f"An error occurred: {e}")
