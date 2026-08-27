"""
Synthesizer node — writes the final cited report. Uses Groq.
"""

from llm_utils import call_llm

_SYNTHESIS_PROMPT = """You are a research analyst writing a report. Using ONLY the evidence
provided below, write a structured report answering the question. Do not use any
outside knowledge — if the evidence doesn't cover something, say so rather than
guessing.

Structure your report with these sections:
1. Summary (2-3 sentences)
2. Key Findings (bullet points, cite sources by number like [1], [2])
3. Limitations (what the evidence doesn't cover)

Question: {query}

Evidence:
{evidence}
"""


def synthesize(state: dict) -> dict:
    query = state.get("original_query", "")
    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        return {
            "final_report": "No evidence was retrieved for this question. "
                                   "Unable to generate a grounded report."
        }

    evidence_lines = []
    for i, c in enumerate(chunks, start=1):
        source = c.get("source_filename", "unknown")
        evidence_lines.append(f"[{i}] (source: {source}) {c['text'][:400]}")
    evidence_text = "\n\n".join(evidence_lines)

    prompt = _SYNTHESIS_PROMPT.format(query=query, evidence=evidence_text)
    report_text = call_llm(prompt).strip()

    return {"final_report": report_text}


if __name__ == "__main__":
    test_state = {
        "original_query": "What are EV battery degradation challenges?",
        "retrieved_chunks": [
            {"text": "Battery degradation affects EV range over time due to capacity fade from repeated charge cycles.",
             "source_filename": "GlobalEVOutlook2024.pdf"},
            {"text": "Ultrasonic methods can detect internal battery damage before visible failure occurs.",
             "source_filename": "2601.08075v2.pdf"},
        ],
    }

    result = synthesize(test_state)
    print("Synthesizer output:\n")
    print(result["final_report"])