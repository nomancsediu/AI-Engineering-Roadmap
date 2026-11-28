# Video script: Training vs inference

## Scene 1: What is Training?

On-screen:
- Large datasets
- Gradient descent
- Weight updates

Narration:

Training is the process where the model learns from data by adjusting its internal weights using gradient descent.

## Scene 2: What is Inference?

On-screen:
- Fixed weights
- Prompt to response
- Low latency

Narration:

Inference uses the trained model to generate answers for new prompts, keeping the weights unchanged.

## Scene 3: Hardware Needs

On-screen:
- GPUs/TPUs for training
- CPU or single GPU for inference

Narration:

Training demands massive parallel hardware, while inference can run on much smaller resources.

## Scene 4: Cost Comparison

On-screen:
- One‑time training cost
- Ongoing per‑request inference cost

Narration:

Training is a big upfront expense; inference incurs continuous costs based on usage.

## Scene 5: From Theory to Product

On-screen:
- Fine‑tune once
- Serve via API
- Scale with load balancers

Narration:

In production you fine‑tune a model once, then expose it through an API that handles inference at scale.
