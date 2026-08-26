import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

REWRITE_PROMPT = """You are a query rewriting assistant. A research sub-question was searched but the retrieved evidence was graded as insufficient.

Original sub-question: {sub_question}
Grader's feedback: {grade_reasoning}
Grader's score: {grade_score}

Rewrite the sub-question to be more specific, more searchable, and more likely to retrieve relevant evidence. Keep it as a single clear question. Return ONLY the rewritten question, nothing else."""

def rewrite_query(state: dict) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")

    sub_question = state.get("current_sub_question", state.get("sub_questions", [""])[0])
    grade_reasoning = state.get("grade_reasoning", "No specific feedback provided.")
    grade_score = state.get("grade_score", 0.0)

    prompt = REWRITE_PROMPT.format(
        sub_question=sub_question,
        grade_reasoning=grade_reasoning,
        grade_score=grade_score
    )

    response = model.generate_content(prompt)
    rewritten = response.text.strip()

    retry_count = state.get("retry_count", 0) + 1

    state["rewritten_query"] = rewritten
    state["retry_count"] = retry_count

    return state


if __name__ == "__main__":
    test_state = {
        "current_sub_question": "What are EV battery problems?",
        "grade_reasoning": "Too vague — evidence retrieved was generic and didn't address specific degradation mechanisms.",
        "grade_score": 0.35,
        "retry_count": 0
    }
    result = rewrite_query(test_state)
    print("Rewriter output:")
    print("  rewritten_query:", result["rewritten_query"])
    print("  retry_count:", result["retry_count"])