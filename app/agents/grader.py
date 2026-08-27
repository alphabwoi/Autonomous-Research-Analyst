"""
Grader node — judges evidence quality. Uses Groq.
"""

import json
from llm_utils import call_llm

_GRADER_PROMPT = """You are an evidence quality grader for a research system. Given a
question and a set of retrieved evidence snippets, judge how well the evidence
covers the question.

Score from 0.0 to 1.0 based on:
- Relevance: does the evidence actually address the question?
- Completeness: is enough evidence present, or are there obvious gaps?
- Redundancy: is the evidence repetitive without adding new information?

A score >= 0.6 means the evidence is good enough to write an answer from.
A score < 0.6 means a retry (different search query) is recommended.

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "grade_score": 0.0 to 1.0,
  "grade_passed": true or false,
  "reasoning": "one short sentence explaining the score"
}}

Question: {query}

Evidence snippets:
{evidence}
"""


def grade(state: dict) -> dict:
    query = state.get("original_query", "")
    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        return {
            "grade_score": 0.0,
            "grade_passed": False,
            "grade_reasoning": "No evidence retrieved.",
        }

    evidence_text = "\n".join(
        f"- [{c.get('retrieval_source', 'unknown')}] {c['text'][:200]}"
        for c in chunks[:10]
    )

    prompt = _GRADER_PROMPT.format(query=query, evidence=evidence_text)
    raw_text = call_llm(prompt).strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"WARNING: Grader got unparseable response, using fallback. Raw: {raw_text[:200]}")
        parsed = {"grade_score": 0.4, "grade_passed": False, "reasoning": "Parse error fallback."}

    return {
        "grade_score": parsed.get("grade_score", 0.0),
        "grade_passed": parsed.get("grade_passed", False),
        "grade_reasoning": parsed.get("reasoning", ""),
    }


if __name__ == "__main__":
    test_state = {
        "original_query": "What are EV battery degradation challenges?",
        "retrieved_chunks": [
            {"text": "Battery degradation affects EV range over time due to capacity fade.", "retrieval_source": "local"},
            {"text": "Ultrasonic methods can detect internal battery damage before failure.", "retrieval_source": "local"},
        ],
    }

    result = grade(test_state)
    print("Grader output:")
    for key, value in result.items():
        print(f"  {key}: {value}")