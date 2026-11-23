# pip install tiktoken openai
import os, json
import tiktoken  # token counting library from OpenAI
import openai

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def chunk_text(text, max_tokens=4000, overlap=200):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        end = i + max_tokens
        chunk = tokens[i:end]
        chunks.append(enc.decode(chunk))
        i = end - overlap  # step back for overlap
    return chunks

def summarize_chunk(chunk):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize the following text in two sentences:\n\n{chunk}"}]
    )
    return response.choices[0].message.content.strip()

# Example usage
with open("report.txt", "r", encoding="utf-8") as f:
    long_text = f.read()

if count_tokens(long_text) > 4000:
    parts = chunk_text(long_text)
    summaries = [summarize_chunk(p) for p in parts]
    final_prompt = "Combine these summaries into a single short abstract:\n" + "\n".join(summaries)
    final = summarize_chunk(final_prompt)
else:
    final = summarize_chunk(long_text)

print("Final abstract:", final)
