"""
Full agent graph. Planner -> Router -> Retriever -> Grader ->
(retry loop back to Retriever, or) -> Synthesizer -> Report Compiler -> END
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "agents"))

from langgraph.graph import StateGraph, END

from state import ResearchState, create_initial_state
from planner import plan
from router import route
from retriever_node import retrieve_evidence
from grader import grade
from rewriter import rewrite_query, should_retry
from synthesizer import synthesize
from report_compiler import compile_report


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", plan)
    graph.add_node("router", route)
    graph.add_node("retriever", retrieve_evidence)
    graph.add_node("grader", grade)
    graph.add_node("rewriter", rewrite_query)
    graph.add_node("synthesizer", synthesize)
    graph.add_node("report_compiler", compile_report)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")
    graph.add_edge("router", "retriever")
    graph.add_edge("retriever", "grader")

    graph.add_conditional_edges(
        "grader",
        should_retry,
        {"retry": "rewriter", "synthesize": "synthesizer"},
    )
    graph.add_edge("rewriter", "retriever")

    graph.add_edge("synthesizer", "report_compiler")
    graph.add_edge("report_compiler", END)

    return graph.compile()


def run_query(query: str) -> dict:
    app = build_graph()
    initial_state = create_initial_state(query)
    return app.invoke(initial_state)


if __name__ == "__main__":
    test_query = "What are the main challenges in EV battery degradation?"
    print(f"Query: {test_query}\n")
    result = run_query(test_query)

    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result.get("final_report", "No report generated."))
    print(f"\nRetries used: {result.get('retry_count', 0)}")
    print(f"Chunks retrieved (final): {len(result.get('retrieved_chunks', []))}")
    print(f"Final grade: {result.get('grade_score')} / passed={result.get('grade_passed')}")
    print(f"Route decision: {result.get('route_decision')}")