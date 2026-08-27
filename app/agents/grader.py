"""
Grader node — runs after the Retriever. Uses an LLM to judge whether
the retrieved evidence is good enough to answer the question, or if
a retry (query rewrite) is needed.

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
    """
    LangGraph node function. Grades state["retrieved_chunks"] against
    state["original_query"] (or sub_questions if present).
    """
    query = state.get("original_query", "")
    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        # Nothing was retrieved at all — automatic fail, no need to call the LLM.
        return {
            "grade_score": 0.0,
            "grade_passed": False,
        }

    # Keep the prompt small — just short previews, not full chunk text,
    # to save tokens on this repeated grading call.
    evidence_text = "\n".join(
        f"- [{c.get('retrieval_source', 'unknown')}] {c['text'][:200]}"
        for c in chunks[:10]  # cap at 10 to keep prompt size sane
    )

    prompt = _GRADER_PROMPT.format(query=query, evidence=evidence_text)
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
        print(f"WARNING: Grader got unparseable response, using fallback. Raw: {raw_text[:200]}")
        # Fail safe: assume it needs a retry rather than silently passing bad evidence
        parsed = {"grade_score": 0.4, "grade_passed": False, "reasoning": "Parse error fallback."}

    return {
        "grade_score": parsed.get("grade_score", 0.0),
        "grade_passed": parsed.get("grade_passed", False),
        "grade_reasoning": parsed.get("reasoning", ""),
    }


if __name__ == "__main__":
    # Quick manual test — requires GOOGLE_API_KEY in .env
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