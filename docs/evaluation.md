# Evaluation — Methodology & Results

## 1. Research Question

Does adding planning, routing, self-grading, and retry logic to a RAG pipeline
produce measurably better-grounded answers than a simple retrieve-then-generate
baseline — and at what cost in latency?

## 2. What Was Compared

| | Baseline RAG | Agentic Pipeline |
|---|---|---|
| Steps | Query → Retrieve (top 5) → LLM → Answer | Plan → Route → Retrieve → Grade → Rewrite (if needed, up to 2x) → Synthesize → Compile |
| Self-checks evidence quality | No | Yes |
| Can retry on poor evidence | No | Yes (max 2 retries) |
| Query decomposition | No | Yes (sub-questions) |
| Source routing (local/web/both) | No (local only) | Yes |

Both pipelines use the same underlying LLM (Groq, `openai/gpt-oss-120b`), the
same vector database (ChromaDB with the same indexed EV document corpus), and
the same embedding model — so any difference in output comes from the
pipeline logic, not the underlying model or data.

## 3. Retrieval Quality

Measured with a hand-labeled test set of 4 queries, each paired with the
document(s) known to be relevant. Metrics computed at k=5.

| Query | Precision@5 | Recall@5 | Reciprocal Rank |
|---|---|---|---|
| EV battery degradation challenges | 1.00 | 0.50 | 1.00 |
| EV charging infrastructure & adoption | 0.20 | 1.00 | 1.00 |
| Ultrasonic battery monitoring methods | 1.00 | 1.00 | 1.00 |
| Tesla's battery sustainability approach | 1.00 | 1.00 | 1.00 |

**Aggregate:**
- **Mean Precision@5: 0.80**
- **Mean Recall@5: 0.875**
- **MRR: 1.00**

**Interpretation:** the correct document was ranked first in every single test
query (MRR of 1.00), and on average 80% of the top-5 retrieved chunks came
from a genuinely relevant source. The one weak spot — the charging
infrastructure query, precision 0.20 — happened because several documents in
the corpus discuss EV charging tangentially, so the retriever surfaced
topically-related-but-not-the-labeled-primary-source chunks. This is a
labeling granularity issue as much as a retrieval weakness — the retrieved
chunks were not irrelevant, just not the single document we pre-labeled as
"the" answer.

## 4. Agent Performance

Measured by running 3 representative queries through both pipelines and
timing/logging each run.

| Metric | Baseline | Agentic |
|---|---|---|
| Avg latency | 4.8s | 39.14s |
| Avg retries | n/a | 0.67 |
| Grade pass rate (first attempt or after retry) | n/a | 67% |

**Speed tradeoff:** the agentic pipeline is **~8.2x slower** than the
baseline. This is expected and by design — the agentic pipeline makes 4-7+
separate LLM calls per query (Planner, Router, Grader, possibly Rewriter,
Synthesizer) versus the baseline's single call, plus it retrieves and
processes more evidence per query (up to 11 chunks per sub-question vs. 5
total for baseline).

## 5. Qualitative Comparison

Sample query: *"What are the main challenges in EV battery degradation?"*

**Baseline output:** a single-pass answer built from the first 5 retrieved
chunks, regardless of whether those chunks were the best available match.
No indication of confidence or evidence quality.

**Agentic output:** the same question was broken into 2 targeted
sub-questions (degradation mechanisms; usage/environmental/manufacturing
factors), evidence was pulled from 12 chunks across 5 distinct source
documents, graded at 0.55 (passing), and the final report explicitly listed
a **Limitations** section noting what the evidence did *not* cover (e.g.
calendar vs. cycle aging, temperature-specific data) — something the
baseline has no mechanism to surface.

This limitations-awareness is the single clearest qualitative advantage of
the agentic approach: it does not just answer confidently regardless of
evidence gaps, it explicitly flags them.

## 6. Conclusion

The agentic pipeline trades roughly 8x latency for:
- Explicit self-assessment of evidence quality (grade score, visible to the user)
- The ability to retry with a reformulated query when evidence is weak
- Multi-source, multi-angle evidence gathering via sub-question decomposition
- Transparent limitations reporting in the final output

For a research-assistant use case — where answer quality and traceability
matter more than sub-10-second response time — this tradeoff favors the
agentic approach. For a use case demanding near-instant responses (e.g. a
live chat widget), the baseline's speed would be the better fit.

## 7. Limitations of This Evaluation

- Retrieval test set is small (4 queries) and relevance judgments are
  single-document-level, hand-labeled by the project team rather than by
  independent annotators — some subjectivity in what counts as "relevant."
- Agent performance benchmark used only 3 queries; latency and retry rate
  will vary with query complexity and corpus size.
- No user study was conducted comparing perceived answer quality between
  the two pipelines — this evaluation is metric-based, not human-preference-based.
- Grader itself is an LLM call, so its scoring has the same reliability
  characteristics (and potential inconsistency) as any LLM judgment.

## 8. How to Reproduce

```
# Retrieval metrics (Precision@K, Recall@K, MRR)
python app/evaluation/retrieval_metrics.py

# Agent performance (latency, retries, pass rate) + baseline comparison
python app/evaluation/benchmarks.py
```

Both scripts must be run from the project root with the virtual environment
activated and a populated ChromaDB index (`data/chroma/`) already present.
