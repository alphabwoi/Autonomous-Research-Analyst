"""
Router node — decides HOW to retrieve evidence for the query.
Runs after the Planner. Uses the Planner's initial guess
(retrieval_strategy, needs_freshness) plus its own lightweight check
to make the final routing decision.

This is a "node" in LangGraph terms: a function that takes the
current state, does work, and returns updates to merge into state.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel("gemini-3.6-flash")

_ROUTER_PROMPT = """You are a routing assistant for a research system. You are given:
- A user's question
- A retrieval strategy guess from an earlier planning step
- Whether the question likely needs current/recent information

Decide the FINAL routing decision from these options:
- "local": use only the local document library (good for stable, established topics)
- "web": use only live web search (good for current events, recent prices, breaking news)
- "both": use both local documents AND web search (good for questions needing both
  background context and current data)
- "clarify": the question is too vague/ambiguous to route confidently

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "route_decision": "local" or "web" or "both" or "clarify",
  "route_reasoning": "one short sentence explaining why"
}}

Question: {query}
Planner's initial guess: {strategy}
Needs freshness: {freshness}
"""


def route(state: dict) -> dict:
    """
    LangGraph node function. Takes the current state (after Planner has run),
    calls the LLM to make the final routing decision.
    """
    query = state["original_query"]
    strategy_guess = state.get("retrieval_strategy", "local")
    needs_freshness = state.get("needs_freshness", False)

    prompt = _ROUTER_PROMPT.format(
        query=query,
        strategy=strategy_guess,
        freshness=needs_freshness,
    )

    response = _model.generate_content(prompt)
    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"WARNING: Router got unparseable response, using fallback. Raw: {raw_text[:200]}")
        parsed = {
            "route_decision": strategy_guess if strategy_guess else "local",
            "route_reasoning": "Fallback: used planner's initial guess due to parse error.",
        }

    return {
        "route_decision": parsed.get("route_decision", "local"),
        "route_reasoning": parsed.get("route_reasoning", ""),
    }


if __name__ == "__main__":
    # Quick manual test — requires GOOGLE_API_KEY in .env
    # Simulates what state would look like after Planner has already run.
    test_state = {
        "original_query": "What are the latest EV battery degradation challenges?",
        "retrieval_strategy": "both",
        "needs_freshness": True,
    }

    result = route(test_state)
    print("Router output:")
    for key, value in result.items():
        print(f"  {key}: {value}")