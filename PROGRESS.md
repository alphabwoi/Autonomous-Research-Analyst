# Progress Log — Autonomous Research Analyst

## Status: Week 3 core complete, entering Week 4

## Completed

### Phase 0 — Setup
- [x] Project folder + venv (Python 3.14.7)
- [x] Full folder structure scaffolded
- [x] Git initialized, .gitignore added
- [x] requirements.txt written and installed
- [x] GitHub repo connected, Aayush added as collaborator
- [x] Domain selected: EV Technology

### Week 1 — Ingestion + Retrieval
- [x] loaders.py, chunker.py, metadata.py (Mohit)
- [x] embeddings.py, vector_store.py, retriever.py (Aayush)
- [x] Verified end-to-end with real EV PDFs, ChromaDB working

### Week 2 — Planner + Router
- [x] state.py: shared ResearchState model
- [x] planner.py: breaks query into sub-questions, flags freshness need
- [x] router.py: decides local/web/both/clarify routing (Aayush)
- [x] rag_tool.py, web_search.py: tool wrappers, excludes reddit/quora/pinterest (Aayush)
- [x] graph.py: LangGraph wiring Planner -> Router -> END
- [x] Verified: compound query correctly split and routed

### Week 3 — Retrieval, Grading, Synthesis
- [x] retriever_node.py: wires rag_tool/web_search into graph
- [x] grader.py: evaluates evidence quality (0.0-1.0 score)
- [x] rewriter.py: rewrites query on low grade, retry loop with MAX_RETRIES=2
- [x] synthesizer.py: writes cited report from evidence
- [x] report_compiler.py: final structured report with references
- [x] Full graph verified end-to-end: query -> plan -> route -> retrieve ->
      grade -> retry (up to 2x) -> synthesize -> compiled report with citations
- [x] Switched LLM provider: Gemini -> Groq (openai/gpt-oss-120b), due to
      Gemini free-tier daily limit (20 requests/day too restrictive)
- [x] llm_utils.py: shared Groq call wrapper with retry/spacing logic
- [x] Expanded corpus: 3 -> ~15+ EV documents (arXiv papers, IEA reports,
      Tesla impact reports, industry whitepapers)
- [x] Reindexed ChromaDB with expanded corpus, retrieval quality improved
      (multiple distinct sources now cited per report)

## Known Issues / Notes
- Grade scores running low (0.1-0.2) even with decent retrieved evidence —
  grader may be too strict, or rewriter's rewritten queries becoming overly
  academic/complex and hurting retrieval match. Not blocking; system still
  produces real cited reports. Worth tuning grader threshold or rewriter
  prompt later if time allows.
- data/raw/ PDFs got committed to git (one file 53MB, near GitHub's 50MB
  warning threshold). Should add data/raw/ to .gitignore and keep PDFs
  local-only going forward — repo bloat risk otherwise.
- Using Windows cmd (not PowerShell) throughout — commands given accordingly.
- Each collaborator uses their own .env / API keys (Groq + Tavily), never shared.

## Next Steps — Week 4
- [ ] Fix .gitignore to exclude data/raw/ (stop committing large PDFs)
- [ ] Build Streamlit UI (frontend/streamlit_app.py) — query input, report display
- [ ] Build FastAPI backend (app/main.py, app/api/routes.py)
- [ ] Containerize with Docker (Dockerfile, docker-compose.yml)
- [ ] Build baseline RAG (simple Query -> Retrieve -> LLM -> Report, no agent loop)
      for comparison against the agentic pipeline
- [ ] Run evaluation: retrieval metrics (Precision@K, Recall@K, MRR)
- [ ] Run evaluation: agent performance (avg retries, route accuracy, latency, cost)
- [ ] Compare baseline vs agentic pipeline results, write up in docs/evaluation.md

## Next Steps — Documentation (buffer, after Week 4)
- [ ] README.md, docs/architecture.md, docs/setup.md, docs/user-guide.md,
      docs/developer-guide.md, docs/evaluation.md, project report, slides,
      demo script, future-scope doc