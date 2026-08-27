"""
Baseline RAG — simple, non-agentic pipeline for comparison against
the full agent. No planning, no routing, no grading, no retries.

Query -> Retrieve -> LLM -> Answer. That's it.
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "tools"))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "agents"))

from rag_tool import rag_search
from llm_utils import call_llm

_BASELINE_PROMPT = """Answer the following question using only the evidence provided below.
Do not use outside knowledge.

Question: {query}

Evidence:
{evidence}

Answer:
"""


def run_baseline(query: str, top_k: int = 5) -> dict:
    """
    Runs the simple baseline pipeline. Returns the answer plus
    the chunks used, for comparison against the agentic pipeline.
    """
    chunks = rag_search(query, top_k=top_k)

    if not chunks:
        return {"answer": "No evidence found.", "chunks_used": 0}

    evidence_text = "\n\n".join(
        f"[{i}] {c['text'][:400]}" for i, c in enumerate(chunks, start=1)
    )

    prompt = _BASELINE_PROMPT.format(query=query, evidence=evidence_text)
    answer = call_llm(prompt).strip()

    return {"answer": answer, "chunks_used": len(chunks)}


if __name__ == "__main__":
    test_query = "What are the main challenges in EV battery degradation?"
    print(f"Query: {test_query}\n")

    result = run_baseline(test_query)
    print(f"Answer:\n{result['answer']}")
    print(f"\nChunks used: {result['chunks_used']}")