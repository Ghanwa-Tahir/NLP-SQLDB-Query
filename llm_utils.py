import ollama

def generate_answer(question, context_df):
    if context_df.empty:
        return "No relevant data found."
    context = context_df.to_string(index=False)
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant that answers questions based on the provided context.'},
            {'role': 'user', 'content': prompt}
        ]
    )
    return response['message']['content']