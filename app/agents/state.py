"""
Shared state definition for the LangGraph agent.
Every node (planner, router, retriever, grader, etc.) reads from
and writes to this same state object as it flows through the graph.
"""

from typing import TypedDict, Optional


class ResearchState(TypedDict, total=False):
    """
    total=False means all fields are optional — nodes fill them in
    progressively as the graph runs. Not every field exists at every step.
    """

    # --- Input ---
    original_query: str  # the user's raw question

    # --- Set by Planner ---
    sub_questions: list[str]        # query broken into smaller pieces
    needs_freshness: bool           # does this need current/recent info?
    retrieval_strategy: str         # "local", "web", or "both" (Planner's initial guess)

    # --- Set by Router ---
    route_decision: str             # final decision: "local", "web", "both", "clarify"
    route_reasoning: str            # short explanation of why, for debugging/traceability

    # --- Set by Retriever ---
    retrieved_chunks: list[dict]    # evidence pulled from local RAG and/or web search

    # --- Set by Grader (Week 3) ---
    grade_score: Optional[float]
    grade_passed: Optional[bool]

    # --- Set by Rewriter (Week 3) ---
    retry_count: int
    rewritten_query: Optional[str]

    # --- Set by Synthesizer (Week 3) ---
    final_report: Optional[str]


def create_initial_state(query: str) -> ResearchState:
    """
    Build a fresh state object for a new user query.
    Every field that hasn't run yet is set to a sensible default.
    """
    return ResearchState(
        original_query=query,
        sub_questions=[],
        needs_freshness=False,
        retrieval_strategy="",
        route_decision="",
        route_reasoning="",
        retrieved_chunks=[],
        grade_score=None,
        grade_passed=None,
        retry_count=0,
        rewritten_query=None,
        final_report=None,
    )


if __name__ == "__main__":
    # Quick manual test
    state = create_initial_state("What are the main EV battery degradation challenges?")
    print("Initial state created:")
    for key, value in state.items():
        print(f"  {key}: {value}")