# Video script: Tokenization

## Scene 1: What is Tokenization?

On-screen:
- Definition of tokens
- Why models need tokens

Narration:

Tokenization turns human language into numbers a model can read. Without it, the model would have no way to process raw text.

## Scene 2: Types of Tokenizers

On-screen:
- Whitespace
- BPE
- WordPiece
- Unigram

Narration:

Different tokenizers balance vocabulary size and language coverage. We'll compare the most common ones.

## Scene 3: Special Tokens

On-screen:
- [CLS], [SEP], [PAD]
- Role in prompts and batching

Narration:

Special tokens tell the model where a sequence starts, ends, or how to pad shorter inputs.

## Scene 4: Tokenization in an API Call

On-screen:
- Encode input
- Send IDs
- Decode output

Narration:

When you call an LLM API, your text is first tokenized, then the model works on IDs, and finally you detokenize the response.

## Scene 5: Practical Tips

On-screen:
- Count tokens for cost
- Avoid truncation
- Cache tokenized prompts

Narration:

Understanding token counts helps control costs and prevents unexpected truncation of your prompts.
