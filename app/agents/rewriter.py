"""
Rewriter node — rewrites query when grader fails. Uses Groq.
"""

from llm_utils import call_llm

_REWRITER_PROMPT = """The following research question did not return good enough search
results. Rewrite it as a SHORTER, SIMPLER question using different keywords —
plain, direct search-engine-style phrasing, not academic jargon. Keep it under
15 words. Do not add extra technical qualifiers or conditions.

Respond with ONLY the rewritten question, no explanation, no quotes.

Original question: {query}
Grader's feedback: {grade_reasoning}
"""

MAX_RETRIES = 2


def rewrite_query(state: dict) -> dict:
    query = state.get("rewritten_query") or state.get("original_query", "")
    grade_reasoning = state.get("grade_reasoning", "No specific feedback provided.")
    current_retries = state.get("retry_count", 0)

    prompt = _REWRITER_PROMPT.format(query=query, grade_reasoning=grade_reasoning)
    new_query = call_llm(prompt).strip().strip('"')

    return {
        "rewritten_query": new_query,
        "sub_questions": [new_query],
        "retry_count": current_retries + 1,
    }


def should_retry(state: dict) -> str:
    grade_passed = state.get("grade_passed", False)
    retry_count = state.get("retry_count", 0)

    if grade_passed:
        return "synthesize"
    if retry_count >= MAX_RETRIES:
        return "synthesize"
    return "retry"


if __name__ == "__main__":
    test_state = {
        "original_query": "EV batteries",
        "grade_reasoning": "Too vague, evidence was generic.",
        "retry_count": 0,
    }

    result = rewrite_query(test_state)
    print("Rewriter output:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    print(f"\nshould_retry decision: {should_retry({**test_state, **result, 'grade_passed': False})}")