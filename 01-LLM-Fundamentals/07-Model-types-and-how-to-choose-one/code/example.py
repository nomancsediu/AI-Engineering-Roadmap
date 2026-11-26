# pip install openai pinecone-client torch transformers
import os, json
from openai import OpenAI
import pinecone
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load API keys from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Initialize clients
client = OpenAI(api_key=openai_api_key)
pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")
index = pinecone.Index("faq-index")

# Load a small instruction‑tuned model locally
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

def embed_text(text):
    # Use OpenAI embedding endpoint
    resp = client.embeddings.create(model="text-embedding-ada-002", input=text)
    return resp.data[0].embedding

def retrieve_faq(query, top_k=3):
    vec = embed_text(query)
    results = index.query(vector=vec, top_k=top_k, include_metadata=True)
    return [r.metadata["answer"] for r in results.matches]

def generate_answer(query, context):
    prompt = f"You are a helpful e‑commerce assistant. Use the following context to answer the question.\nContext: {context}\nQuestion: {query}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=150)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Example usage
user_question = "What is the return policy for electronics?"
faq_context = " ".join(retrieve_faq(user_question))
answer = generate_answer(user_question, faq_context)
print(answer)
