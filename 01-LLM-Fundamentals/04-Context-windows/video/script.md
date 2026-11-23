# Video script: Context windows

## Scene 1: Introducing Context Windows

On-screen:
- Definition of tokens
- Why models need a fixed window

Narration:

In this scene we define what a token is and explain that large language models can only look at a limited number of them at once.

## Scene 2: Token Counting Basics

On-screen:
- Rough 4 characters per token
- Tools to count tokens

Narration:

We show how to estimate token counts and introduce a simple Python library for exact counting.

## Scene 3: When Input Exceeds the Window

On-screen:
- Chunking strategy
- Summarization fallback

Narration:

If your prompt is too long, you either split it into overlapping chunks or compress it with a summarizer.

## Scene 4: Practical Prompt Design

On-screen:
- Prioritize recent info
- Use system messages wisely

Narration:

Tips on arranging your prompt so the most important context stays inside the window.

## Scene 5: Real Product Examples

On-screen:
- Chat bots keep recent turns
- RAG pipelines retrieve passages

Narration:

We close by showing how context windows shape chat assistants and document search tools.
