# pip install openai tiktoken
import os, json
import openai
import tiktoken

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example text to summarize
article = """Your long article text goes here..."""

# Choose model and pricing (example rates)
model = "gpt-3.5-turbo"
price_per_1k_input = 0.002   # USD
price_per_1k_output = 0.002  # USD

# Tokenize input
enc = tiktoken.encoding_for_model(model)
input_tokens = len(enc.encode(article))

# Build prompt
prompt = f"Summarize the following article in 2 sentences:\n\n{article}"
prompt_tokens = len(enc.encode(prompt))

# Call the API
response = openai.ChatCompletion.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=150
)

# Count output tokens
output_text = response.choices[0].message.content
output_tokens = len(enc.encode(output_text))

# Compute cost
cost = (prompt_tokens / 1000) * price_per_1k_input + (output_tokens / 1000) * price_per_1k_output

print(json.dumps({
    "prompt_tokens": prompt_tokens,
    "output_tokens": output_tokens,
    "total_cost_usd": round(cost, 6),
    "summary": output_text
}, indent=2))
