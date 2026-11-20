import os, re, json, time, sys, urllib.request, urllib.error

GROQ_KEY = os.environ["GROQ_API_KEY"]
MODEL = "openai/gpt-oss-120b"
PER_DAY = 1
NOTE_LANGUAGE = "simple English"

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# A trailing * means this topic also gets a mini project.
ROADMAP = [
    ("LLM Fundamentals", [
        "What is an LLM", "How LLMs generate text", "Tokenization*",
        "Context windows", "Sampling: temperature, top-p, top-k",
        "Hallucinations", "Model types and how to choose one",
        "Token pricing and cost*", "Training vs inference",
    ]),
    ("Prompt and Context Engineering", [
        "Prompt engineering basics", "Zero-shot and few-shot prompting",
        "Chain-of-thought prompting", "System prompts and roles",
        "Prompt templates", "Context engineering", "Prompt testing*",
    ]),
    ("Structured Output and Tool Calling", [
        "Structured outputs and JSON mode", "Pydantic validation*",
        "Function and tool calling*", "Tool schema design",
        "Error handling and retries",
    ]),
    ("Embeddings and Vector Databases", [
        "What are embeddings", "Similarity metrics", "Vector database concepts",
        "FAISS*", "Chroma*", "ANN indexes and HNSW", "pgvector",
        "Semantic search*",
    ]),
    ("RAG", [
        "RAG overview", "Document loading and parsing", "Chunking strategies",
        "Retrieval strategies", "Hybrid search", "Reranking",
        "Query rewriting", "Build a RAG pipeline*", "Advanced RAG patterns",
    ]),
    ("RAG Evaluation", [
        "Retrieval metrics", "Faithfulness and answer relevance",
        "Building a test set", "LLM-as-judge", "Evaluation pipeline*",
    ]),
    ("Agents, MCP and Memory", [
        "What is an AI agent", "ReAct pattern", "Agentic workflow patterns",
        "Planning and reasoning", "Memory systems", "LangGraph basics*",
        "Model Context Protocol (MCP)*", "Multi-agent systems", "Agent evaluation",
    ]),
    ("Fine-tuning", [
        "Fine-tuning vs RAG", "Dataset preparation", "LoRA and QLoRA",
        "Fine-tuning workflow*", "Quantization and distillation",
    ]),
    ("Evaluation and Observability", [
        "Tracing LLM apps", "Logging and monitoring", "Regression testing for LLMs",
        "Feedback loops",
    ]),
    ("Deployment, Cost and Streaming", [
        "Streaming responses*", "Caching", "Latency optimization",
        "Cost optimization", "Rate limits and reliability", "Model serving and vLLM",
        "Deploying an LLM app with Docker*", "Scaling LLM apps",
    ]),
    ("Safety and Guardrails", [
        "Prompt injection", "Guardrails*", "PII and data privacy",
        "Jailbreaks and red teaming", "Reducing hallucinations", "Responsible AI",
    ]),
    ("Multimodal AI", [
        "Vision language models", "Speech to text", "Text to speech",
        "Multimodal RAG*",
    ]),
    ("System Design and Interview Prep", [
        "AI system design framework", "Design a chat-with-documents system",
        "Design a customer support agent", "Trade-offs: cost, latency, quality",
        "Behavioral and project storytelling", "Capstone project*",
    ]),
]

PROGRESS_FILE = "progress.json"
TOTAL = sum(len(t) for _, t in ROADMAP)

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FFFF\U00002600-\U000027BF\U00002300-\U000023FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U0000200D]+"
)


class ApiError(Exception):
    pass


def slugify(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def strip_emoji(x):
    if isinstance(x, str):
        return EMOJI_RE.sub("", x)
    if isinstance(x, list):
        return [strip_emoji(i) for i in x]
    if isinstance(x, dict):
        return {k: strip_emoji(v) for k, v in x.items()}
    return x


def post(url, payload, headers, retries=3):
    headers = {"User-Agent": BROWSER_UA, "Accept": "application/json", **headers}
    for attempt in range(retries):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
        try:
            return json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            print("HTTP ERROR", e.code, e.read().decode()[:400])
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(30 * (attempt + 1))
                continue
            raise ApiError(f"HTTP {e.code}")
        except Exception as e:
            print("Network error:", e)
            if attempt < retries - 1:
                time.sleep(10)
                continue
            raise ApiError(str(e))


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        return json.load(open(PROGRESS_FILE, encoding="utf-8"))
    return []


def pick_next(progress):
    done = {p["key"] for p in progress}
    for mi, (module, topics) in enumerate(ROADMAP, 1):
        for ti, raw in enumerate(topics, 1):
            key = f"{mi}-{ti}"
            if key not in done:
                return mi, ti, module, raw.rstrip("*"), raw.endswith("*"), key
    return None


KEYS = ["summary", "fundamentals", "workflow_mermaid", "example", "video_scenes",
        "code", "takeaways", "interview_qa"]


def ask_groq(module, topic, with_project):
    project_rule = (
        '"mini_project": object with keys "title", "goal", "steps" (list of 4-7 strings), '
        '"files" (list of file names), "stretch" (string),'
        if with_project else '"mini_project": null,'
    )
    prompt = f"""You are an expert AI engineering teacher writing a study note for a learner who knows Python and backend basics but is new to AI engineering (building apps with LLMs). Skip ML and deep learning theory unless the topic itself needs it.
Module: {module}
Topic: {topic}
Write in {NOTE_LANGUAGE}. Be accurate, practical and interview oriented. Do NOT use any emojis.

Reply ONLY with a JSON object with these keys:
"summary": one sentence definition,
"fundamentals": markdown string, 200-300 words, explain from scratch, use **bold** for key terms, short paragraphs or bullets, and end with 1-2 sentences on where it is used in real AI products,
"workflow_mermaid": a valid Mermaid flowchart (start with 'flowchart TD'), 5-9 nodes, every node label in double quotes like A["Text"], no special characters inside labels, no code fences,
"example": markdown string, one concrete real-life example explained step by step,
"video_scenes": list of 5-6 objects {{"title": string, "bullets": list of 2-3 short strings, "narration": string of 2-3 spoken sentences}},
"code": a short, runnable Python example (20-50 lines) with helpful comments. Prefer standard library or very common packages and say in a comment at top which packages are needed with pip install. If an API key is needed, read it from an environment variable. No markdown fences,
"takeaways": list of 3 short strings,
{project_rule}
"interview_qa": list of 5 objects {{"q": string, "a": string of 2-4 sentences}}"""
    for _ in range(3):
        res = post(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                "model": MODEL,
                "temperature": 0.3,
                "max_tokens": 9000,
                "reasoning_effort": "low",
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": prompt}],
            },
            {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_KEY}"},
        )
        try:
            d = json.loads(res["choices"][0]["message"]["content"])
            for k in KEYS:
                assert k in d, f"missing {k}"
            assert len(d["interview_qa"]) >= 3 and len(d["video_scenes"]) >= 3
            return strip_emoji(d)
        except Exception as e:
            print("Bad JSON, retrying...", e)
            time.sleep(5)
    raise ApiError("Groq did not return valid JSON")


def clean_code(s):
    s = re.sub(r"^```[a-zA-Z]*\n", "", s.strip())
    return re.sub(r"\n```$", "", s).strip() + "\n"


def clean_mermaid(s):
    s = re.sub(r"^```[a-zA-Z]*\n", "", s.strip())
    return re.sub(r"\n```$", "", s).strip()


def bullets(items):
    return "\n".join(f"- {i}" for i in items)


def numbered(items):
    return "\n".join(f"{n}. {s}" for n, s in enumerate(items, 1))


def build_readme(mi, ti, module, topic, d):
    scenes = numbered([s["title"] for s in d["video_scenes"]])
    qa = "\n\n".join(f"**Q{n}. {x['q']}**\n\n{x['a']}" for n, x in enumerate(d["interview_qa"], 1))
    out = f"""# {topic}

| | |
|:--|:--|
| **Module** | {mi}. {module} |
| **Topic** | {ti} |
| **Code** | [code/example.py](./code/example.py) |
| **Video script** | [video/script.md](./video/script.md) |

> {d['summary']}

---

## Fundamentals

{d['fundamentals']}

---

## Workflow

```mermaid
{clean_mermaid(d['workflow_mermaid'])}
```

---

## Example

{d['example']}

---

## Video

**Watch:** coming soon.

**Scenes**

{scenes}

Full narration: [video/script.md](./video/script.md)

---

## Code

```python
{clean_code(d['code']).strip()}
```

File: [code/example.py](./code/example.py)
"""
    mp = d.get("mini_project")
    if mp:
        out += f"""
---

## Mini Project: {mp['title']}

**Goal:** {mp['goal']}

**Steps**

{numbered(mp['steps'])}

**Files to create:** {', '.join(f'`{f}`' for f in mp['files'])}

**Stretch:** {mp['stretch']}

Build this yourself and commit it inside the `project/` folder of this topic.
"""
    out += f"""
---

## Key Takeaways

{bullets(d['takeaways'])}

---

## Interview Questions

{qa}

---

> AI-generated study note. Verify important details with official documentation.
"""
    return out


def build_script(topic, d):
    L = [f"# Video script: {topic}", ""]
    for n, s in enumerate(d["video_scenes"], 1):
        L += [f"## Scene {n}: {s['title']}", "", "On-screen:", bullets(s["bullets"]), "",
              "Narration:", "", s["narration"], ""]
    return "\n".join(L)


def save(progress):
    json.dump(progress, open(PROGRESS_FILE, "w", encoding="utf-8"), indent=2)
    n = len(progress)
    pct = round(100 * n / TOTAL)
    filled = int(30 * n / TOTAL)
    L = ["# Progress", "", f"`[{'#' * filled}{'.' * (30 - filled)}]` **{n} / {TOTAL}** topics ({pct}%)", ""]
    nxt = pick_next(progress)
    if nxt:
        L += [f"**Up next:** {nxt[3]} ({nxt[2]})", ""]
    for mi, (module, topics) in enumerate(ROADMAP, 1):
        items = [p for p in progress if p["module_index"] == mi]
        L += [f"## {mi}. {module} ({len(items)} / {len(topics)})", ""]
        if items:
            L += ["| # | Topic | Notes |", "|--:|:------|:------|"]
            for p in items:
                L.append(f"| {p['topic_index']} | {p['topic']} | [Open](./{p['path']}/README.md) |")
        else:
            L.append("_Coming soon..._")
        L.append("")
    open("PROGRESS.md", "w", encoding="utf-8").write("\n".join(L))


def main():
    progress = load_progress()
    made = 0
    error = False
    while made < PER_DAY:
        nxt = pick_next(progress)
        if not nxt:
            print("All topics done!")
            break
        mi, ti, module, topic, with_project, key = nxt
        print("Next:", module, "|", topic)
        try:
            d = ask_groq(module, topic, with_project)
        except ApiError as e:
            print("Stopped:", e)
            error = True
            break
        folder = f"{mi:02d}-{slugify(module)}/{ti:02d}-{slugify(topic)}"
        os.makedirs(f"{folder}/code", exist_ok=True)
        os.makedirs(f"{folder}/video", exist_ok=True)
        if with_project:
            os.makedirs(f"{folder}/project", exist_ok=True)
            open(f"{folder}/project/.gitkeep", "w").close()
        open(f"{folder}/README.md", "w", encoding="utf-8").write(build_readme(mi, ti, module, topic, d))
        open(f"{folder}/code/example.py", "w", encoding="utf-8").write(clean_code(d["code"]))
        open(f"{folder}/video/script.md", "w", encoding="utf-8").write(build_script(topic, d))
        progress.append({"key": key, "module_index": mi, "topic_index": ti,
                         "module": module, "topic": topic, "path": folder})
        save(progress)
        print("Created", folder)
        made += 1
    if error and made == 0:
        sys.exit(1)


main()
