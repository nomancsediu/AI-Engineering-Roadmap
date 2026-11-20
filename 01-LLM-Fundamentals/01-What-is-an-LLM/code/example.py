# pip install openai
import os, json
from openai import OpenAI

# Read API key from environment
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

prompt = "Explain the benefits of using LLMs in customer support."
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=150,
    temperature=0.7,
)

print("Assistant:", response.choices[0].message.content.strip())
