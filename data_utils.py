from dotenv import load_dotenv
load_dotenv()
import sqlite3
import os
from langchain_core.documents import Document

DB_PATH = os.getenv("DATA_PATH", "Data.db")  # Make sure .env has: DATA_PATH=Data.db

def get_all_rows():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Replace 'users' with your actual table name if needed
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # Get column names
    column_names = [desc[0] for desc in cursor.description]
    
    conn.close()
    
    return [dict(zip(column_names, row)) for row in rows]

def make_document(row: dict) -> Document:
    content = ", ".join(f"{k}: {v}" for k, v in row.items())
    metadata = {"employee_id": row.get("employee_id", "N/A")}
    return Document(page_content=content, metadata=metadata)

def make_documents() -> list[Document]:
    rows = get_all_rows()
    return [make_document(row) for row in rows]
