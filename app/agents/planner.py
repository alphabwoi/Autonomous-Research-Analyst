"""
Planner node — first step in the agent graph. Uses Groq (Llama 3.3 70B)
to break the query into sub-questions and decide retrieval strategy.
"""

import json
from llm_utils import call_llm

_PLANNER_PROMPT = """You are a research planning assistant. Given a user's research question, do two things:

1. Break the question into 1-3 focused sub-questions that together would fully answer it.
   If the question is already simple/specific, just return it as a single sub-question.
2. Decide if this question needs CURRENT/RECENT information (news, prices, latest models,
   recent events) or if it's about STABLE knowledge (established facts, technical concepts,
   historical data) that a local document library would cover.

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "sub_questions": ["question 1", "question 2"],
  "needs_freshness": true or false,
  "retrieval_strategy": "local" or "web" or "both"
}}

User question: {query}
"""


def plan(state: dict) -> dict:
    query = state["original_query"]
    prompt = _PLANNER_PROMPT.format(query=query)

    raw_text = call_llm(prompt).strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"WARNING: Planner got unparseable response, using fallback. Raw: {raw_text[:200]}")
        parsed = {
            "sub_questions": [query],
            "needs_freshness": False,
            "retrieval_strategy": "local",
        }

    return {
        "sub_questions": parsed.get("sub_questions", [query]),
        "needs_freshness": parsed.get("needs_freshness", False),
        "retrieval_strategy": parsed.get("retrieval_strategy", "local"),
    }


if __name__ == "__main__":
    from state import create_initial_state

    test_state = create_initial_state(
        "What are the latest EV battery degradation challenges and how do they compare to older lithium-ion research?"
    )

    result = plan(test_state)
    print("Planner output:")
    for key, value in result.items():
        print(f"  {key}: {value}")