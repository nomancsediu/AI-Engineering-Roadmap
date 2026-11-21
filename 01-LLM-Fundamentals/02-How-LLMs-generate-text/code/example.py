import os
import json
import requests

# pip install requests
# Set your OpenAI API key in the environment variable OPENAI_API_KEY
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise EnvironmentError('OPENAI_API_KEY not set')

endpoint = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

prompt = "Write a concise 30‑word product description for a waterproof Bluetooth speaker."
payload = {
    'model': 'gpt-3.5-turbo',
    'messages': [{'role': 'user', 'content': prompt}],
    'max_tokens': 60,
    'temperature': 0.7,
    'n': 1
}

response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
response.raise_for_status()
result = response.json()
generated_text = result['choices'][0]['message']['content']
print('Generated description:')
print(generated_text.strip())
