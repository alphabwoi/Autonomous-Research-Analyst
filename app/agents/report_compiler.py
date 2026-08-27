from datetime import datetime

def compile_report(state: dict) -> dict:
    original_query = state.get("original_query", "Untitled Query")
    synthesized_answer = state.get("synthesized_answer", "")
    sub_questions = state.get("sub_questions", [])
    evidence = state.get("evidence", {})

    sources = set()
    for items in evidence.values():
        for item in items:
            sources.add(item.get("source", "unknown"))

    report_lines = []
    report_lines.append(f"# Research Report")
    report_lines.append(f"\n**Query:** {original_query}")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append(f"\n## Sub-questions investigated")
    for sq in sub_questions:
        report_lines.append(f"- {sq}")
    report_lines.append(f"\n## Findings\n")
    report_lines.append(synthesized_answer)
    report_lines.append(f"\n## Sources")
    for src in sorted(sources):
        report_lines.append(f"- {src}")

    final_report = "\n".join(report_lines)
    state["final_report"] = final_report

    return state


if __name__ == "__main__":
    test_state = {
        "original_query": "What are the main challenges in EV battery degradation, and what's the latest news on solid-state batteries?",
        "sub_questions": [
            "What are the primary causes and technical challenges of EV battery degradation?",
            "What is the latest news and recent developments regarding solid-state batteries for electric vehicles?"
        ],
        "synthesized_answer": "EV battery degradation is primarily driven by lithium plating, SEI layer growth, and cathode cracking [Source: local_doc_12]. Fast charging worsens this due to heat and plating risk [Source: local_doc_7]. On the solid-state front, Toyota announced a pilot production line in August 2026 targeting 2027 vehicle integration [Source: web_toyota_2026].",
        "evidence": {
            "q1": [{"source": "local_doc_12", "content": "..."}, {"source": "local_doc_7", "content": "..."}],
            "q2": [{"source": "web_toyota_2026", "content": "..."}]
        }
    }
    result = compile_report(test_state)
    print(result["final_report"])