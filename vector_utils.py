from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from data_utils import get_all_rows, make_documents
import pandas as pd

def build_vectorstore():
    df = get_all_rows()
    docs = make_documents(df)
    documents = [Document(page_content=doc, metadata={"row_idx": i}) for i, doc in enumerate(docs)]
    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
    vectorstore = Chroma.from_documents(documents, embedding=embeddings, persist_directory="chroma_db")
    return vectorstore, pd.DataFrame(df)  # Convert to DataFrame here

def semantic_search(query, vectorstore, df, top_k=5):
    if not hasattr(df, "iloc"):
        raise TypeError(f"Expected df to be a pandas DataFrame, but got {type(df)}")

    results = vectorstore.similarity_search(query, k=top_k)
    indices = [doc.metadata["row_idx"] for doc in results]
    return df.iloc[indices]


