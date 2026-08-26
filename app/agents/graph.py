"""
The agent graph — wires together all the nodes (Planner, Router, and
later Retriever/Grader/Rewriter/Synthesizer) into a single LangGraph
state machine.

Run this file directly to test Planner -> Router end to end.
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "agents"))

from langgraph.graph import StateGraph, END

from state import ResearchState, create_initial_state
from planner import plan
from router import route


def build_graph():
    """
    Constructs the LangGraph state machine.
    Currently: Planner -> Router -> END
    (Retriever, Grader, Rewriter, Synthesizer will be added in Week 3)
    """
    graph = StateGraph(ResearchState)

    # Register nodes — each is a function(state) -> dict of updates
    graph.add_node("planner", plan)
    graph.add_node("router", route)

    # Wire the flow: entry -> planner -> router -> end
    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")
    graph.add_edge("router", END)

    return graph.compile()


def run_query(query: str) -> dict:
    """
    Convenience function: run a query through the full graph so far.
    """
    app = build_graph()
    initial_state = create_initial_state(query)
    final_state = app.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    test_query = "What are the main challenges in EV battery degradation, and what's the latest news on solid-state batteries?"

    print(f"Query: {test_query}\n")
    result = run_query(test_query)

    print("=" * 60)
    print("FINAL STATE AFTER PLANNER -> ROUTER")
    print("=" * 60)
    print(f"Sub-questions: {result['sub_questions']}")
    print(f"Needs freshness: {result['needs_freshness']}")
    print(f"Planner's strategy guess: {result['retrieval_strategy']}")
    print(f"Router's final decision: {result['route_decision']}")
    print(f"Router's reasoning: {result['route_reasoning']}")