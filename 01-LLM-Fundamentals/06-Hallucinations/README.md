# Hallucinations

| | |
|:--|:--|
| **Module** | 1. LLM Fundamentals |
| **Topic** | 6 |
| **Code** | [code/example.py](./code/example.py) |
| **Video script** | [video/script.md](./video/script.md) |

> Hallucination is when an LLM generates information that sounds plausible but is false or unsupported by its training data.

---

## Fundamentals

## Hallucinations in LLMs
- **Definition**: A hallucination occurs when a language model produces output that is factually incorrect, fabricated, or unrelated to the prompt, yet presented with confidence.
- **Why it happens**: LLMs predict the next token based on statistical patterns, not truth. When the training data lacks reliable evidence or the prompt is ambiguous, the model fills gaps with plausible‑sounding text.
- **Types**:
  - *Factual hallucination*: Wrong dates, names, numbers.
  - *Logical hallucination*: Contradicts earlier statements in the same response.
  - *Contextual hallucination*: Inserts details that were never mentioned.
- **Mitigation strategies**:
  - **Prompt engineering**: Ask the model to cite sources or say "I don't know" when uncertain.
  - **Retrieval‑augmented generation (RAG)**: Pull relevant documents first, then let the model synthesize.
  - **Post‑processing checks**: Use validators, regex, or external APIs to verify claims.
  - **Temperature control**: Lower temperature reduces creative but risky completions.
- **Evaluation**: Metrics like factual consistency scores, human fact‑checking, or automated fact‑check APIs help measure hallucination rates.

LLM hallucinations appear in chat assistants, code generators, and content‑creation tools, so developers must design safeguards before shipping.


---

## Workflow

```mermaid
flowchart TD
A[User Prompt] --> B[LLM Generates Draft]
B --> C[Retrieval Module (optional)]
C --> D[Combine Retrieval + Draft]
D --> E[Post‑Processing Validator]
E --> F{Is Output Verified?}
F -- Yes --> G[Return to User]
F -- No --> H[Regenerate or Flag]
H --> B
```

---

## Example

### Real‑life Example: Customer Support Chatbot
1. **User asks**: "What is the warranty period for Model X?"
2. **Bot retrieves** the product spec sheet from a database (RAG step).
3. **LLM drafts** a response: "Model X comes with a 2‑year warranty."
4. **Validator** checks the spec sheet; it actually says 3 years.
5. **Post‑processor** replaces the incorrect claim with the correct one and adds a citation: "Model X comes with a **3‑year** warranty (see spec sheet)."
6. **Final answer** is sent back to the user, eliminating the hallucination.


---

## Video

**Watch:** [Open video](https://github.com/nomancsediu/AI-Engineering-Roadmap/releases/tag/video-1-6)

**Scenes**

1. What is Hallucination?
2. Types of Hallucinations
3. Prompt Engineering Tricks
4. Retrieval‑Augmented Generation
5. Post‑Processing Validation
6. Real Product Example

Full narration: [video/script.md](./video/script.md)

---

## Code

```python
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
```

File: [code/example.py](./code/example.py)

---

## Key Takeaways

- Hallucinations are false outputs that arise from statistical token prediction.
- Retrieval‑augmented generation and post‑processing validation are the most effective safeguards.
- Prompt engineering can reduce hallucinations but never eliminates them completely.

---

## Interview Questions

**Q1. What is a hallucination in the context of LLMs?**

A hallucination is when the model generates information that sounds plausible but is factually incorrect or unsupported by its training data.

**Q2. Why do LLMs hallucinate even when they have seen correct facts during training?**

Because the model predicts the next token based on statistical patterns, not truth. When the prompt is ambiguous or the data is sparse, it fills gaps with likely‑looking text that may be wrong.

**Q3. Name two practical ways to reduce hallucinations in a production chatbot.**

Use retrieval‑augmented generation to fetch up‑to‑date documents before generation, and apply a post‑processing validator that checks facts against a trusted source.

**Q4. How does temperature affect hallucination risk?**

Higher temperature makes the model sample more diverse tokens, increasing creativity but also the chance of fabricating details. Lower temperature yields more deterministic, conservative outputs.

**Q5. What role does prompt engineering play in mitigating hallucinations?**

Prompt engineering can steer the model to say "I don't know" when uncertain, request citations, or limit the scope of the answer, thereby reducing the likelihood of invented facts.

---

> AI-generated study note. Verify important details with official documentation.
