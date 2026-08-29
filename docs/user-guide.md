# User Guide

How to use the Autonomous Research Analyst once it's running.

## Accessing the App

After following the [setup guide](setup.md), open your browser to:
```
http://localhost:8501
```

## The Interface

The app has three parts:

1. **Mode selector** — choose between:
   - **Agentic Pipeline** — the full system: plans, routes, retrieves,
     grades evidence, retries if needed, and writes a cited report
   - **Baseline RAG** — a simple retrieve-then-answer pipeline, useful for
     comparing against the agentic pipeline's output

2. **Question box** — type your research question here

3. **Run Research button** — submits the question and displays results

## Asking a Good Question

This system is built around an **EV Technology** knowledge base. Questions
work best when they're about electric vehicles, batteries, charging
infrastructure, or related topics — since that's what the underlying
documents cover.

**Good examples:**
- "What are the main challenges in EV battery degradation?"
- "How does EV charging infrastructure affect adoption rates?"
- "What is Tesla's approach to battery sustainability?"

**Less effective:**
- Questions entirely unrelated to EVs — the system will say it found no
  relevant evidence rather than making something up
- Extremely broad questions ("tell me about cars") — more specific
  questions retrieve more targeted evidence

## Reading the Results

### Agentic Pipeline Mode

You'll see a structured report with:
- **Summary** — a short overview of the answer
- **Key Findings** — bullet points, each citing a source number like `[1]`
- **Limitations** — what the evidence does *not* cover (this is intentional
  and important — the system is telling you where its answer might be
  incomplete)
- **References** — which source document each citation number refers to

Expand **"Pipeline details"** to see:
- **Route decision** — did it search local documents, the web, or both?
- **Retries used** — how many times it reformulated the query because
  evidence wasn't good enough on the first try
- **Final grade score** — the self-assessed evidence quality (0.0–1.0)

### Baseline RAG Mode

A simpler answer with no self-grading or retry information — just the
answer and how many evidence chunks were used to write it.

## Why Two Modes?

The Baseline mode exists so you can directly compare a "dumb" pipeline
against the full agentic one. Try asking the same question in both modes —
you'll typically see the agentic version cite more diverse sources and
explicitly flag gaps in the evidence, while the baseline just answers
confidently regardless of evidence quality.

## Response Time

The agentic pipeline is slower than the baseline (typically 30-45 seconds
vs. under 5 seconds) because it makes multiple AI calls per question
(planning, routing, grading, possibly retrying, then writing the final
answer) rather than just one. This is expected — the tradeoff is answer
quality and transparency for speed.

## Common Issues

**"Could not connect to the backend"** — the FastAPI server isn't running.
See the [setup guide](setup.md) for how to start it.

**Answer says "no evidence found"** — your question is likely outside the
EV Technology domain the knowledge base covers, or phrased in a way that
doesn't match the indexed documents well. Try rephrasing or asking
something more directly related to EVs/batteries/charging.
