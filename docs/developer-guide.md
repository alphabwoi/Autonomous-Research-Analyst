# Developer Guide

For anyone working on or extending this codebase.

## Codebase Map

```
app/
├── main.py              FastAPI app — HTTP endpoints
├── agents/               the LangGraph agent, one file per node
├── ingestion/             PDF → chunks pipeline
├── retrieval/             chunks → searchable vector store
├── tools/                 wrappers the agent calls (RAG, web search)
└── evaluation/            baseline RAG + metrics scripts
frontend/
└── streamlit_app.py      the UI, talks to app/main.py over HTTP
```

See [PROJECT_DOCUMENTATION.md](../PROJECT_DOCUMENTATION.md) for a full
explanation of what each file does.

## Core Design Pattern: LangGraph Nodes

Every agent step (`planner.py`, `router.py`, `grader.py`, etc.) follows the
same shape:

```python
def some_node(state: dict) -> dict:
    # read whatever you need from state
    query = state["original_query"]

    # do the work (usually an LLM call via llm_utils.call_llm)

    # return ONLY the fields you're updating — LangGraph merges
    # this into the shared state automatically
    return {"some_field": some_value}
```

**Important:** a node can only update fields that exist in `state.py`'s
`ResearchState` TypedDict. If you add a new field a node should write,
you must add it to `ResearchState` first — otherwise LangGraph silently
drops the update (this caused a real bug during development; see
`PROJECT_DOCUMENTATION.md` section 8 known issues, or check git history
around the `synthesized_answer` vs `final_report` field mismatch).

## Adding a New Node

1. Create the file in `app/agents/`, following the pattern above
2. Add any new state fields it needs to `state.py`
3. Import it in `graph.py`
4. Add it with `graph.add_node("name", function)`
5. Wire edges with `graph.add_edge(...)` (or `add_conditional_edges` for branching logic)
6. Test standalone first: put a `if __name__ == "__main__":` block with
   sample input, run `python your_file.py` directly before wiring into the graph

## Adding a New Tool

Tools live in `app/tools/` and are simple functions the agent calls — they
don't know anything about LangGraph state, just take clean arguments and
return clean data. See `rag_tool.py` and `web_search.py` for the pattern.

## LLM Calls

All LLM calls go through `app/agents/llm_utils.py`'s `call_llm(prompt)`
function — never call the Groq client directly in a node. This gives you
automatic retry-on-failure and call spacing to avoid rate limits, in one
place, for free.

## Working with the Vector Store

- `app/retrieval/embeddings.py` — turns text into vectors (local model, no API cost)
- `app/retrieval/vector_store.py` — ChromaDB storage/search
- `app/retrieval/retriever.py` — the clean interface everything else should use

Don't import ChromaDB or the embedding model directly elsewhere in the
codebase — always go through `retriever.py`'s `retrieve()` function.

## Running Tests

```bash
# Full ingestion + retrieval integration test
python tests/test_week1_integration.py

# Retrieval quality metrics
python app/evaluation/retrieval_metrics.py

# Agent performance benchmarks (baseline vs agentic)
python app/evaluation/benchmarks.py

# Any individual node, standalone
python app/agents/planner.py
python app/agents/grader.py
# etc.
```

## Git Workflow Used on This Project

Feature branches per component, merged into `main` once tested:
```bash
git checkout main
git pull origin main
git checkout -b your-feature-branch
# ... do work, test it ...
git add <files>
git commit -m "Clear description"
git push origin your-feature-branch
# then merge into main once confirmed working
```

**Never commit `.env` or hardcoded API keys.** If GitHub's push protection
blocks a push for a detected secret, don't just re-add the file — rotate
the exposed key immediately (it's compromised the moment it's written to
disk in a commit, even if the push itself was blocked), then remove it
from the file and recommit.

## Known Rough Edges (as of last update)

- Grader scores can run lower than expected on thin evidence — tuned once
  already (see `grader.py`'s prompt, increased evidence-per-query in
  `retriever_node.py`) but may need further tuning as the corpus grows.
- Free-tier LLM rate limits (Groq: ~8000 tokens/min) can be hit during
  heavy testing (e.g. running `benchmarks.py` back-to-back). The retry
  logic in `llm_utils.py` handles this automatically but adds latency.
- Large PDF files should never be committed to git — `data/raw/` is
  git-ignored for this reason. Keep it that way.

## Extending to a New Domain

The system isn't EV-specific in its code — only the ingested documents and
the ChromaDB collection name (`ev_research`, set in `vector_store.py` and
`rag_tool.py`) are domain-specific. To repurpose for a different domain:
1. Replace documents in `data/raw/`
2. Change the collection name if you want a separate index
3. Re-run the ingestion pipeline
4. Update the domain string in `app/ingestion/metadata.py`
