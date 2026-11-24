# Video script: Sampling: temperature, top-p, top-k

## Scene 1: Why sampling matters

On-screen:
- Deterministic vs random output
- Impact on user experience

Narration:

We start by seeing how the same prompt can produce very different answers depending on sampling settings.

## Scene 2: Temperature explained

On-screen:
- Scale logits
- Low vs high values

Narration:

Temperature multiplies the logits before softmax, making the distribution sharper or flatter.

## Scene 3: Top‑k and top‑p basics

On-screen:
- Cut off low‑probability tokens
- Cumulative probability

Narration:

Top‑k keeps the k most likely tokens, while top‑p keeps enough tokens to reach a probability threshold.

## Scene 4: Combining the knobs

On-screen:
- Typical defaults
- When to adjust each

Narration:

Most APIs let you combine temperature with either top‑k or top‑p to fine‑tune output style.

## Scene 5: Real product demo

On-screen:
- Chatbot response
- Creative writing tool

Narration:

We show a live demo of a chatbot where changing these parameters changes the tone and creativity of replies.
