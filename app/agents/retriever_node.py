"""
Retriever node — runs after the Router. Based on route_decision
("local", "web", "both", or "clarify"), calls the appropriate
tool(s) and collects evidence into state.

This is a "node" in LangGraph terms: a function that takes the
current state, does work, and returns updates to merge into state.
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "tools"))

from rag_tool import rag_search
from web_search import web_search


def retrieve_evidence(state: dict) -> dict:
    """
    LangGraph node function. Uses state["route_decision"] and
    state["sub_questions"] to gather evidence chunks from the
    right source(s).
    """
    route_decision = state.get("route_decision", "local")
    sub_questions = state.get("sub_questions", [state.get("original_query", "")])

    all_chunks = []

    for question in sub_questions:
        if route_decision in ("local", "both"):
            local_results = rag_search(question, top_k=3)
            for r in local_results:
                r["retrieval_source"] = "local"
                r["sub_question"] = question
            all_chunks.extend(local_results)

        if route_decision in ("web", "both"):
            web_results = web_search(question, max_results=3)
            for r in web_results:
                r["retrieval_source"] = "web"
                r["sub_question"] = question
                # normalize field name so grader/synthesizer don't need
                # to care whether a chunk came from local or web
                r.setdefault("similarity_distance", None)
            all_chunks.extend(web_results)

        if route_decision == "clarify":
            # No retrieval — the graph should ideally stop and ask the
            # user to clarify. For now we just leave chunks empty so
            # downstream nodes can detect this case.
            pass

    return {"retrieved_chunks": all_chunks}


if __name__ == "__main__":
    # Quick manual test — simulates state after Router has run
    test_state = {
        "original_query": "What are EV battery degradation challenges?",
        "sub_questions": ["What are EV battery degradation challenges?"],
        "route_decision": "local",
    }

    result = retrieve_evidence(test_state)
    chunks = result["retrieved_chunks"]
    print(f"Retrieved {len(chunks)} chunks:")
    for c in chunks:
        source = c.get("source_filename", "unknown")
        print(f"  - [{c['retrieval_source']}] [{source}] {c['text'][:120]}...")
