import ollama
from data_utils import sample_column_values

def build_prompt(user_query, schema_info, schema_samples):
    schema_desc = ""
    for table, schema in schema_info.items():
        schema_desc += f"Table: {table}\nColumns:\n"
        for col in schema["columns"]:
            samples = schema_samples.get(table, {}).get(col["name"], [])
            sample_values = ", ".join(f'"{val}"' for val in samples if isinstance(val, str)) or "..."
            schema_desc += f" - {col['name']} ({col['type']}, purpose: {col.get('purpose', 'unknown')}, examples: {sample_values})\n"

    guidance =     guidance = """RULES FOR SQL QUERY GENERATION:

1. Always prioritize using fuzzy search with LIKE '%term%' for general terms.
2. If a term may appear in multiple columns, apply multiple OR conditions:
   WHERE col1 LIKE '%term%' OR col2 LIKE '%term%' OR ...
3. Use LIKE primarily on columns with purpose 'label', 'classification', or 'location'.
4. Avoid using exact equality (=) unless user explicitly specifies a value.
5. Avoid columns with purpose 'identifier' or 'timestamp' unless explicitly requested.
6. JOIN tables only when necessary, based on inferred or matching keys.
7. Use only the provided tables and columns — no assumptions.
8. Never respond with explanations or commentary — return only the raw SQL.
"""

    return f"Schema:\n{schema_desc}\n\nUser query:\n{user_query}\n\n{guidance}"

def generate_sql(natural_language_query, schema_info, db_path, prompt_suffix=""):
    schema_samples = {}
    for table, schema in schema_info.items():
        schema_samples[table] = {}
        for col in schema["columns"]:
            values = sample_column_values(db_path, table, col["name"])
            schema_samples[table][col["name"]] = values

    prompt = build_prompt(f"{natural_language_query} {prompt_suffix}".strip(), schema_info, schema_samples)

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are an expert SQL developer."},
                {"role": "user", "content": prompt}
            ],
            options={"temperature": 0.1}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise ValueError(f"LLM error: {str(e)}")

def generate_answer(question, results_df):
    if results_df.empty:
        return "I couldn't find any data matching your question."

    summary = results_df.to_string(index=False)

    prompt = f"""
You are a helpful data assistant. Answer the user's question based on this data.

Question: {question}

Data:
{summary}

Guidelines:
- Be natural and clear
- Use LIKE synonym logic if needed
- Mention if data looks incomplete
- Don't just list — summarize helpfully
"""

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            options={"temperature": 0.5}
        )
        return response["message"]["content"]
    except Exception as e:
        return f"I couldn't generate an answer due to: {str(e)}"
