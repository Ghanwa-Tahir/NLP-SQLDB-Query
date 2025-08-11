import streamlit as st
import tempfile
import sqlite3
import pandas as pd
from llm_utils import generate_sql, generate_answer
from schema_tags import annotate_column_purpose

st.set_page_config(page_title="SQL Natural Chatbot", page_icon="🧠")
st.title("🧠 SQL Natural Chatbot")

if "db_connection" not in st.session_state:
    st.session_state.db_connection = None
if "schema_info" not in st.session_state:
    st.session_state.schema_info = None

with st.sidebar:
    st.header("Connect to Database")
    uploaded_file = st.file_uploader("Choose a SQLite database file", type=["db", "sqlite"])
    
    if uploaded_file:
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            temp_file.write(uploaded_file.read())
            temp_file.close()
            
            # Connect to SQLite database
            conn = sqlite3.connect(temp_file.name)
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            if not tables:
                st.error("No tables found!")
                st.stop()
            
            # Get schema info with annotated purposes
            schema_info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                schema_info[table] = {
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "purpose": annotate_column_purpose(col[1])
                        }
                        for col in columns
                    ],
                    "primary_key": [col[1] for col in columns if col[5] == 1]
                }
            
            st.session_state.db_connection = temp_file.name
            st.session_state.schema_info = schema_info
            st.success(f"Connected! Found tables: {', '.join(tables)}")
            
        except Exception as e:
            st.error(f"Connection failed: {e}")
            st.stop()

st.subheader("Query the Database in Natural Language")
query = st.text_input("Ask your question:", placeholder="e.g. What are the top student grades?")

if st.button("Submit") and query and st.session_state.schema_info:
    with st.spinner("Thinking..."):
        try:
            # Generate SQL
            sql_query = generate_sql(query, st.session_state.schema_info, st.session_state.db_connection)
            st.text_area("📝 SQL Preview", sql_query, height=150)
            
            # Execute query
            conn = sqlite3.connect(st.session_state.db_connection)
            results = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            # Show results
            st.dataframe(results)
            
            # Generate natural language answer
            answer = generate_answer(query, results)
            st.write(answer)
            
        except Exception as e:
            st.error(f"Error processing your query: {e}")
