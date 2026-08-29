"""
Agent performance benchmarks — measures latency, retry rate, routing
behavior, and LLM call count across a set of test queries. Also runs
the baseline for direct timing comparison.
"""

import os
import sys
import time

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "agents"))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "evaluation"))

from graph import run_query
from baseline_rag import run_baseline

TEST_QUERIES = [
    "What are the main challenges in EV battery degradation?",
    "How does EV charging infrastructure affect adoption?",
    "What is Tesla's approach to battery sustainability?",
]


def benchmark_agentic(queries: list[str]) -> dict:
    results = []

    for query in queries:
        print(f"\nRunning agentic pipeline: {query}")
        start = time.time()
        result = run_query(query)
        elapsed = time.time() - start

        results.append({
            "query": query,
            "latency_seconds": round(elapsed, 2),
            "retry_count": result.get("retry_count", 0),
            "route_decision": result.get("route_decision", ""),
            "grade_score": result.get("grade_score"),
            "grade_passed": result.get("grade_passed"),
            "chunks_retrieved": len(result.get("retrieved_chunks", [])),
            "report_length_chars": len(result.get("final_report", "")),
        })

    avg_latency = sum(r["latency_seconds"] for r in results) / len(results)
    avg_retries = sum(r["retry_count"] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r["grade_passed"]) / len(results)

    return {
        "per_query": results,
        "avg_latency_seconds": round(avg_latency, 2),
        "avg_retries": round(avg_retries, 2),
        "grade_pass_rate": round(pass_rate, 2),
    }


def benchmark_baseline(queries: list[str]) -> dict:
    results = []

    for query in queries:
        print(f"\nRunning baseline pipeline: {query}")
        start = time.time()
        result = run_baseline(query)
        elapsed = time.time() - start

        results.append({
            "query": query,
            "latency_seconds": round(elapsed, 2),
            "chunks_used": result.get("chunks_used", 0),
            "answer_length_chars": len(result.get("answer", "")),
        })

    avg_latency = sum(r["latency_seconds"] for r in results) / len(results)

    return {
        "per_query": results,
        "avg_latency_seconds": round(avg_latency, 2),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("BENCHMARKING BASELINE RAG")
    print("=" * 60)
    baseline_results = benchmark_baseline(TEST_QUERIES)

    print("\n" + "=" * 60)
    print("BENCHMARKING AGENTIC PIPELINE")
    print("=" * 60)
    agentic_results = benchmark_agentic(TEST_QUERIES)

    print("\n" + "=" * 60)
    print("SUMMARY COMPARISON")
    print("=" * 60)
    print(f"Baseline avg latency:  {baseline_results['avg_latency_seconds']}s")
    print(f"Agentic avg latency:   {agentic_results['avg_latency_seconds']}s")
    print(f"Agentic avg retries:   {agentic_results['avg_retries']}")
    print(f"Agentic grade pass rate: {agentic_results['grade_pass_rate'] * 100:.0f}%")
    print(f"\nSpeed tradeoff: agentic pipeline is "
          f"{agentic_results['avg_latency_seconds'] / baseline_results['avg_latency_seconds']:.1f}x "
          f"slower than baseline, in exchange for self-graded, retry-capable evidence.")