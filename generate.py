import os, re, sys, json, time, datetime
import urllib.request, urllib.error

GROQ_KEY = os.environ.get("GROQ_API_KEY")
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
PROGRESS_FILE = "progress.json"
TOPICS_DIR = "topics"

# Ei list ta tumi nijer moto edit korte paro. Upor theke ek ta kore topic nibe.
TOPICS = [
    "Python for AI Engineering",
    "NumPy and Pandas Essentials",
    "Math for Machine Learning: Linear Algebra",
    "Math for Machine Learning: Probability and Statistics",
    "Machine Learning Fundamentals",
    "Supervised vs Unsupervised Learning",
    "Model Evaluation: Metrics, Overfitting, Cross-Validation",
    "Feature Engineering",
    "Scikit-learn Workflow",
    "Neural Networks Basics",
    "Backpropagation and Gradient Descent",
    "Deep Learning with PyTorch",
    "Convolutional Neural Networks",
    "Sequence Models and RNNs",
    "Transformers and Attention",
    "Large Language Models Explained",
    "Prompt Engineering",
    "Embeddings and Vector Databases",
    "Retrieval-Augmented Generation (RAG)",
    "Fine-Tuning LLMs: LoRA and PEFT",
    "AI Agents and Tool Use",
    "Building APIs for AI with FastAPI",
    "Docker for AI Projects",
    "MLOps: Experiment Tracking and Model Registry",
    "Deploying Models to the Cloud",
    "Evaluating and Monitoring LLM Apps",
    "AI Safety and Responsible AI",
    "Building an End-to-End AI Project",
]


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        return json.load(open(PROGRESS_FILE, encoding="utf-8"))
    return []


def groq_json(topic):
    system = (
        "You are an AI engineering teacher. Reply with valid JSON only, no markdown fences. "
        "Schema: {\"summary\": str, \"key_points\": [str], \"scenes\": [{\"title\": str, "
        "\"bullets\": [str], \"narration\": str}]}. "
        "Rules: exactly 6 scenes. Scene title max 6 words. 3 or 4 bullets per scene, "
        "each max 60 characters. Narration: 2 to 3 plain spoken sentences per scene, "
        "no stage directions, no emojis, no markdown, no scene numbers. "
        "Scene 1 introduces the topic, the last scene is a short recap."
    )
    user = f"Create a short beginner-friendly lesson on: {topic}"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_KEY}",
        "User-Agent": "daily-ai-topic/1.0",
    }
    url = "https://api.groq.com/openai/v1/chat/completions"
    for attempt in range(4):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            data = json.loads(r["choices"][0]["message"]["content"])
            if len(data.get("scenes", [])) < 3:
                raise ValueError("too few scenes")
            return data
        except urllib.error.HTTPError as e:
            print("GROQ HTTP ERROR", e.code, e.read().decode()[:300])
            if e.code in (429, 500, 502, 503):
                time.sleep(15 * (attempt + 1))
                continue
            raise
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print("Bad response, retrying...", e)
            time.sleep(5)
    raise RuntimeError("Groq generation failed")


def write_topic(folder, topic, data):
    os.makedirs(os.path.join(folder, "video"), exist_ok=True)

    readme = [f"# {topic}", "", data.get("summary", ""), "", "## Key points"]
    readme += [f"- {k}" for k in data.get("key_points", [])]
    readme += ["", "**Watch:** coming soon.", ""]
    open(os.path.join(folder, "README.md"), "w", encoding="utf-8").write("\n".join(readme))

    out = [f"# {topic}", ""]
    for n, s in enumerate(data["scenes"], 1):
        bullets = "\n".join(f"- {b}" for b in s["bullets"][:4])
        narration = " ".join(s["narration"].split())
        out.append(f"## Scene {n}: {s['title'].strip()}")
        out.append("On-screen:")
        out.append(bullets)
        out.append("Narration:")
        out.append(narration)
        out.append("")
    open(os.path.join(folder, "video", "script.md"), "w", encoding="utf-8").write("\n".join(out))


def main():
    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set. Add it in repo Settings > Secrets > Actions.")
        sys.exit(1)

    progress = load_progress()
    done = {p["topic"] for p in progress}
    remaining = [t for t in TOPICS if t not in done]
    if not remaining:
        print("All topics in TOPICS are done. Add more topics.")
        return

    topic = remaining[0]
    n = len(progress) + 1
    key = f"{n:02d}-{slugify(topic)}"
    folder = os.path.join(TOPICS_DIR, key)

    print("Generating topic:", topic)
    data = groq_json(topic)
    write_topic(folder, topic, data)

    progress.append({
        "key": key,
        "topic": topic,
        "path": folder,
        "date": datetime.date.today().isoformat(),
    })
    json.dump(progress, open(PROGRESS_FILE, "w", encoding="utf-8"), indent=2)
    print("Created:", folder)


main()
