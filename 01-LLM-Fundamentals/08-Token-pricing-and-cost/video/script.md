# Video script: Token pricing and cost

## Scene 1: What are tokens?

On-screen:
- Text broken into sub‑words
- Different from characters or words

Narration:

Tokens are the basic units LLMs understand. A single word can become multiple tokens, especially for rare or compound words.

## Scene 2: How providers price tokens

On-screen:
- Price per 1k input tokens
- Separate rate for output tokens
- Model tier matters

Narration:

Each provider publishes a price sheet. Larger, more capable models cost more per thousand tokens.

## Scene 3: Counting tokens in code

On-screen:
- Install tiktoken
- Encode text to IDs
- len(ids) gives token count

Narration:

We'll show a quick Python snippet that turns any string into a token count using the official tokenizer.

## Scene 4: Estimating cost for a request

On-screen:
- Add input and output tokens
- Multiply by rate
- Round to cents

Narration:

Combine the token counts, apply the per‑thousand price, and you have the monetary cost of the API call.

## Scene 5: Cost‑aware design tips

On-screen:
- Keep prompts concise
- Use smaller models when possible
- Batch requests

Narration:

Practical ways to reduce spend without hurting user experience.
