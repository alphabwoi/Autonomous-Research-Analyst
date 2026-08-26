"""
Planner node — the first step in the agent graph.
Takes the user's raw query and uses an LLM to:
  1. Break it into sub-questions (if complex)
  2. Decide whether it likely needs fresh/current info (web) vs
     stable knowledge (local RAG)

This is a "node" in LangGraph terms: a function that takes the
current state, does work, and returns updates to merge into state.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel("gemini-2.0-flash")

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
    """
    LangGraph node function. Takes the current state, calls the LLM
    to plan, and returns the fields to update in state.
    """
    query = state["original_query"]
    prompt = _PLANNER_PROMPT.format(query=query)

    response = _model.generate_content(prompt)
    raw_text = response.text.strip()

    # Models sometimes wrap JSON in ```json fences — strip if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback if the model doesn't return clean JSON —
        # don't crash the whole pipeline over a formatting hiccup.
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
    # Quick manual test — requires GOOGLE_API_KEY in .env
    from state import create_initial_state

    test_state = create_initial_state(
        "What are the latest EV battery degradation challenges and how do they compare to older lithium-ion research?"
    )

    result = plan(test_state)
    print("Planner output:")
    for key, value in result.items():
        print(f"  {key}: {value}")