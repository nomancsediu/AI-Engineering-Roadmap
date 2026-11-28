# Training vs inference

| | |
|:--|:--|
| **Module** | 1. LLM Fundamentals |
| **Topic** | 9 |
| **Code** | [code/example.py](./code/example.py) |
| **Video script** | [video/script.md](./video/script.md) |

> Training builds a model by adjusting weights on data, while inference uses the trained model to generate predictions.

---

## Fundamentals

## Training vs Inference
- **Training**: The phase where a large language model (LLM) learns patterns from massive text corpora. The system repeatedly feeds batches of data, computes loss, and updates millions or billions of parameters with gradient descent. Training is compute‑heavy, often runs on clusters of GPUs/TPUs for days or weeks, and produces a **checkpoint** that stores the learned weights.
- **Inference**: The phase where the already‑trained checkpoint is loaded to answer user queries or generate text. The model’s weights stay fixed; the system only runs a forward pass to produce logits and then samples or selects tokens. Inference is latency‑sensitive, runs on a single GPU or even CPU, and must be scalable for many concurrent users.
- **Key differences**:
  - Resource usage: training needs massive parallel hardware; inference can be lightweight.
  - Data flow: training consumes labeled or unsupervised text batches; inference consumes a single prompt.
  - Cost: training is a one‑time expense; inference incurs ongoing operational cost per request.
- **Practical tip**: Separate the two pipelines. Use a distributed training framework (e.g., PyTorch Lightning, DeepSpeed) for the training job, and a lightweight serving stack (e.g., FastAPI + vLLM) for inference.

**Real‑world usage**: Companies train LLMs once (or fine‑tune periodically) and then expose them via APIs that handle inference for chatbots, code assistants, and search augmentation.


---

## Workflow

```mermaid
flowchart TD
A[Collect raw text data] --> B[Tokenize and create dataset]
B --> C[Define model architecture]
C --> D[Run training loop on GPU cluster]
D --> E[Save checkpoint]
E --> F[Load checkpoint in serving app]
F --> G[Receive user prompt]
G --> H[Run forward pass (inference)]
H --> I[Return generated response]
```

---

## Example

### Real‑life Example: Customer‑Support Chatbot
1. **Data collection**: Gather past support tickets and chat logs.
2. **Pre‑processing**: Clean text, remove PII, and tokenize.
3. **Fine‑tuning**: Load a base LLM (e.g., Llama‑2) and train on the support data for a few epochs, saving the checkpoint.
4. **Deployment**: Wrap the checkpoint in a FastAPI service that accepts a JSON payload `{ "prompt": "..." }`.
5. **Inference**: When a user asks a question, the service runs a forward pass, decodes the tokens, and returns a helpful answer.
6. **Feedback loop**: Store new interactions to periodically re‑fine‑tune the model for continuous improvement.

---

## Video

**Watch:** [Open video](https://github.com/nomancsediu/AI-Engineering-Roadmap/releases/tag/video-1-9)

**Scenes**

1. What is Training?
2. What is Inference?
3. Hardware Needs
4. Cost Comparison
5. From Theory to Product

Full narration: [video/script.md](./video/script.md)

---

## Code

```python
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
```

File: [code/example.py](./code/example.py)

---

## Key Takeaways

- Training creates the model; inference uses it.
- Training is compute‑intensive, inference is latency‑focused.
- In production you fine‑tune once and serve the model via an API.

---

## Interview Questions

**Q1. What is the main purpose of the training phase for an LLM?**

Training adjusts the model's parameters so it can capture language patterns from large text corpora, turning random weights into a useful predictor.

**Q2. Why is inference usually cheaper per request than training?**

Inference only runs a forward pass with fixed weights, requiring far fewer compute cycles than the iterative backward‑pass and weight updates of training.

**Q3. Name two hardware setups typical for training and inference.**

Training often uses multi‑GPU or TPU clusters; inference can run on a single GPU, CPU, or even specialized inference accelerators.

**Q4. How do you handle scaling inference for many users?**

Deploy the model behind a stateless API, use load balancers, and optionally shard the model across multiple instances or use model‑parallel serving frameworks.

**Q5. What is a checkpoint and why is it important?**

A checkpoint stores the model's learned weights after training; it allows you to reload the model for inference or further fine‑tuning without retraining from scratch.

---

> AI-generated study note. Verify important details with official documentation.
