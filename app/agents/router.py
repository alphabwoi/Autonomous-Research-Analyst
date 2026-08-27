"""
Router node — decides HOW to retrieve evidence. Uses Groq.
"""

import json
from llm_utils import call_llm

_ROUTER_PROMPT = """You are a routing assistant for a research system. You are given:
- A user's question
- A retrieval strategy guess from an earlier planning step
- Whether the question likely needs current/recent information

Decide the FINAL routing decision from these options:
- "local": use only the local document library
- "web": use only live web search
- "both": use both local documents AND web search
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
    query = state["original_query"]
    strategy_guess = state.get("retrieval_strategy", "local")
    needs_freshness = state.get("needs_freshness", False)

    prompt = _ROUTER_PROMPT.format(
        query=query,
        strategy=strategy_guess,
        freshness=needs_freshness,
    )

    raw_text = call_llm(prompt).strip()

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
    test_state = {
        "original_query": "What are the latest EV battery degradation challenges?",
        "retrieval_strategy": "both",
        "needs_freshness": True,
    }

    result = route(test_state)
    print("Router output:")
    for key, value in result.items():
        print(f"  {key}: {value}")