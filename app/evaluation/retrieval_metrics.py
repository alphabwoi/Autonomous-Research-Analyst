"""
Retrieval evaluation metrics — Precision@K, Recall@K, MRR (Mean Reciprocal Rank).

Uses a small hand-labeled test set: queries paired with which source
documents are considered "relevant" ground truth. Since we don't have
official relevance judgments, relevance here is judged by whether the
retrieved chunk's source document is a document we know covers that topic.
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "app", "tools"))

from rag_tool import rag_search

# Test queries paired with the source filename(s) considered relevant.
# Update this list to match whatever documents are actually in data/raw/.
TEST_SET = [
    {
        "query": "What are EV battery degradation challenges?",
        "relevant_sources": ["2608.24397v1.pdf", "2601.08075v2.pdf"],
    },
    {
        "query": "How does EV charging infrastructure affect adoption?",
        "relevant_sources": ["GlobalEVOutlook2024.pdf"],
    },
    {
        "query": "What ultrasonic methods are used to monitor lithium-ion batteries?",
        "relevant_sources": ["2601.08075v2.pdf"],
    },
    {
        "query": "What is Tesla's approach to battery sustainability?",
        "relevant_sources": ["2019-tesla-impact-report.pdf", "2020-tesla-impact-report.pdf"],
    },
]


def precision_at_k(retrieved_sources: list[str], relevant_sources: list[str], k: int) -> float:
    top_k = retrieved_sources[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for s in top_k if s in relevant_sources)
    return hits / len(top_k)


def recall_at_k(retrieved_sources: list[str], relevant_sources: list[str], k: int) -> float:
    top_k = retrieved_sources[:k]
    if not relevant_sources:
        return 0.0
    # Count unique relevant documents found, not raw chunk hits —
    # multiple chunks can come from the same document.
    unique_relevant_found = set(top_k) & set(relevant_sources)
    return len(unique_relevant_found) / len(relevant_sources)


def reciprocal_rank(retrieved_sources: list[str], relevant_sources: list[str]) -> float:
    for i, source in enumerate(retrieved_sources, start=1):
        if source in relevant_sources:
            return 1.0 / i
    return 0.0


def run_evaluation(k: int = 5) -> dict:
    precisions, recalls, rr_scores = [], [], []

    print(f"Running retrieval evaluation (k={k})...\n")

    for item in TEST_SET:
        query = item["query"]
        relevant = item["relevant_sources"]

        results = rag_search(query, top_k=k)
        retrieved_sources = [r["source_filename"] for r in results]

        p = precision_at_k(retrieved_sources, relevant, k)
        r = recall_at_k(retrieved_sources, relevant, k)
        rr = reciprocal_rank(retrieved_sources, relevant)

        precisions.append(p)
        recalls.append(r)
        rr_scores.append(rr)

        print(f"Query: {query}")
        print(f"  Retrieved sources: {retrieved_sources}")
        print(f"  Relevant sources:  {relevant}")
        print(f"  Precision@{k}: {p:.2f} | Recall@{k}: {r:.2f} | Reciprocal Rank: {rr:.2f}\n")

    avg_precision = sum(precisions) / len(precisions)
    avg_recall = sum(recalls) / len(recalls)
    mrr = sum(rr_scores) / len(rr_scores)

    print("=" * 50)
    print("AGGREGATE RESULTS")
    print("=" * 50)
    print(f"Mean Precision@{k}: {avg_precision:.3f}")
    print(f"Mean Recall@{k}:    {avg_recall:.3f}")
    print(f"MRR:                {mrr:.3f}")

    return {"mean_precision": avg_precision, "mean_recall": avg_recall, "mrr": mrr}


if __name__ == "__main__":
    run_evaluation(k=5)