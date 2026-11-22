# pip install tiktoken openai
import os, json
import tiktoken  # OpenAI's tokenizer library
import openai

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Choose the same tokenizer used by gpt-3.5-turbo
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

text = "I received my order yesterday but the package was damaged and the item is missing. Please help."
# Encode to token IDs
token_ids = enc.encode(text)
print("Token IDs:", token_ids)
print("Number of tokens:", len(token_ids))

# Simple summarization prompt
prompt = f"Summarize in one sentence: {text}"
prompt_ids = enc.encode(prompt)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=30,
    temperature=0.2,
)
# Extract generated text
summary = response.choices[0].message.content.strip()
print("Summary:", summary)

# Detokenize the model's raw token IDs (optional demonstration)
# Here we just re‑encode the summary to show round‑trip
summary_ids = enc.encode(summary)
print("Round‑trip IDs match?", summary_ids == enc.encode(summary))
