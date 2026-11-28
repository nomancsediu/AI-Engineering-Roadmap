# pip install transformers torch fastapi uvicorn
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

class Prompt(BaseModel):
    text: str

# Load model and tokenizer once at startup
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

@app.post("/generate")
async def generate(prompt: Prompt):
    inputs = tokenizer(prompt.text, return_tensors="pt")
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return {"response": response}

# To run: uvicorn this_file_name:app --host 0.0.0.0 --port 8000
