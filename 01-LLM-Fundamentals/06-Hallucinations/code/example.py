# pip install openai
import os, json, re
from openai import OpenAI

# Load API key from environment
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

prompt = "What is the warranty period for the Acme Turbo 3000?"

# Step 1: Retrieve spec (simulated here as a dict)
specs = {"Acme Turbo 3000": "3 years warranty, 2 years free support"}
product = "Acme Turbo 3000"
retrieved = specs.get(product, "")

# Step 2: Generate answer with a request to cite source
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer factually and cite the spec if you use it."},
        {"role": "user", "content": prompt}
    ]
)
answer = response.choices[0].message.content.strip()

# Step 3: Simple validator – look for a year number and compare to spec
match = re.search(r"(\d+) year", answer)
if match:
    years = int(match.group(1))
    spec_years = int(re.search(r"(\d+) years", retrieved).group(1))
    if years != spec_years:
        answer = f"The warranty is {spec_years} years (according to the product spec)."

print(json.dumps({"question": prompt, "answer": answer}, ensure_ascii=False, indent=2))
