# Video script: How LLMs generate text

## Scene 1: Intro to Text Generation

On-screen:
- What is a token?
- Why probability matters

Narration:

In this scene we define tokens and explain that LLMs generate text by predicting the next token's probability.

## Scene 2: From Prompt to Tokens

On-screen:
- Tokenization process
- Example prompt

Narration:

We show how a user prompt is broken into sub‑word tokens that the model can understand.

## Scene 3: Transformer Forward Pass

On-screen:
- Self‑attention basics
- Hidden states

Narration:

The token IDs travel through transformer layers, where self‑attention mixes information from the whole context.

## Scene 4: Logits to Words

On-screen:
- Softmax conversion
- Sampling methods

Narration:

Logits are turned into probabilities, and we discuss greedy, top‑k, and nucleus sampling.

## Scene 5: Loop Until Completion

On-screen:
- Appending tokens
- Stopping criteria

Narration:

The newly chosen token is added to the prompt and the cycle repeats until an end‑of‑sentence token or length limit is reached.

## Scene 6: Real‑World Use Cases

On-screen:
- Chatbots
- Content creation

Narration:

We wrap up by highlighting how this pipeline powers chat assistants, code generators, and marketing copy tools.
