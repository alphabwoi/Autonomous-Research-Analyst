import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYNTHESIS_PROMPT = """You are a research synthesis assistant. Given a user's original query, a set of sub-questions, and evidence gathered for each, write a clear, well-organized answer.

Original query: {original_query}

Evidence by sub-question:
{evidence_block}

Write a synthesized answer that addresses the original query directly. Cite sources inline using [Source: X] notation where X is the source identifier given with each piece of evidence. Be factual — only use the evidence provided, do not add outside knowledge."""

def format_evidence_block(evidence: dict) -> str:
    lines = []
    for sub_q, items in evidence.items():
        lines.append(f"\nSub-question: {sub_q}")
        for item in items:
            source = item.get("source", "unknown")
            content = item.get("content", "")
            lines.append(f"  - [Source: {source}] {content}")
    return "\n".join(lines)

def synthesize(state: dict) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")

    original_query = state.get("original_query", "")
    evidence = state.get("evidence", {})

    evidence_block = format_evidence_block(evidence)

    prompt = SYNTHESIS_PROMPT.format(
        original_query=original_query,
        evidence_block=evidence_block
    )

    response = model.generate_content(prompt)
    synthesized_answer = response.text.strip()

    state["synthesized_answer"] = synthesized_answer

    return state


if __name__ == "__main__":
    test_state = {
        "original_query": "What are the main challenges in EV battery degradation, and what's the latest news on solid-state batteries?",
        "evidence": {
            "What are the primary causes and technical challenges of EV battery degradation?": [
                {"source": "local_doc_12", "content": "Battery degradation is primarily caused by lithium plating, SEI layer growth, and cathode particle cracking during charge cycles."},
                {"source": "local_doc_7", "content": "Fast charging accelerates degradation due to increased heat generation and lithium plating risk."}
            ],
            "What is the latest news and recent developments regarding solid-state batteries for electric vehicles?": [
                {"source": "web_toyota_2026", "content": "Toyota announced in August 2026 a pilot production line for solid-state batteries targeting 2027 vehicle integration."}
            ]
        }
    }
    result = synthesize(test_state)
    print("Synthesizer output:")
    print(result["synthesized_answer"])