import os, json, random
import openai  # pip install openai

# Read API key from environment
openai.api_key = os.getenv('OPENAI_API_KEY')

prompt = "Write a friendly 30‑word welcome message for new users of a fitness app."

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8,   # creativity
    top_p=0.9,         # nucleus sampling
    # top_k is not directly exposed in OpenAI API; some providers support it
    max_tokens=60,
    n=1,
    stop=None
)

generated = response['choices'][0]['message']['content']
print("Generated message:")
print(generated)

# Simple function to experiment with parameters
def generate(text, temp=1.0, p=1.0):
    r = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        temperature=temp,
        top_p=p,
        max_tokens=80
    )
    return r['choices'][0]['message']['content']

print("--- Variation with low temperature ---")
print(generate(prompt, temp=0.2, p=0.95))
print("--- Variation with higher temperature ---")
print(generate(prompt, temp=1.2, p=0.9))
