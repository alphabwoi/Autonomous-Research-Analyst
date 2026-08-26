"""
RAG tool — wraps the retriever (app/retrieval/retriever.py) so the
agent graph can call it as a simple "tool" without knowing about
embeddings or ChromaDB internals.
"""

import os
import sys

# Make app/retrieval importable from here
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "retrieval"))

from retriever import retrieve


def rag_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Search the local EV document knowledge base.
    Returns a list of chunk dicts with text, source, and similarity score.
    """
    results = retrieve(query, top_k=top_k, collection_name="ev_research")
    return results


if __name__ == "__main__":
    # Quick manual test — requires the ChromaDB collection to already
    # be populated (run tests/test_week1_integration.py first if not).
    results = rag_search("EV battery degradation challenges", top_k=3)
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"  - ({r['similarity_distance']:.4f}) [{r['source_filename']}] {r['text'][:150]}...")