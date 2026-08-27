\# Progress Log — Autonomous Research Analyst



\## Status: Phase 0 (Setup) — in progress



\## Completed

\- \[x] Project folder + venv created (Python 3.14.7)

\- \[x] Full folder structure scaffolded (app/, frontend/, data/, tests/, docs/)

\- \[x] Git initialized, .gitignore added, first commit made

\- \[x] requirements.txt written and installed (fastapi, langgraph, chromadb, streamlit, sentence-transformers, etc.)

\- \[x] Sanity check passed: fastapi, langgraph, chromadb, streamlit all import correctly



\## Next Steps

\- \[ ] Choose LLM provider (Gemini Flash / OpenAI small / Groq) and add SDK to requirements.txt

\- \[ ] Get API keys: LLM provider + Tavily (web search)

\- \[ ] Create .env from .env.example with real keys

\- \[x] Domain selected: EV Technology

\- \[ ] Start Week 1: ingestion pipeline (loaders, chunker, embeddings, ChromaDB)



\## Notes

\- On Windows using cmd (not PowerShell) — commands given accordingly.

\- Using local ChromaDB, local sentence-transformers embeddings (no OpenAI embedding cost).

\- Full roadmap in roadmap.md (uploaded separately / in project docs).



\## Week 1 — Ingestion (Mohit)

\- \[x] loaders.py — loads PDFs from data/raw, extracts text

\- \[x] chunker.py — splits text into \~1000-char overlapping chunks

\- \[x] metadata.py — enriches chunks with domain, hash, title, preview

\- \[x] Tested end-to-end: 3 EV PDFs → 941 enriched chunks

\- \[ ] Add more EV documents (target 15-25 total, currently have 3)









\## Week 1 — COMPLETE ✅

\- Ingestion (Mohit): loaders.py, chunker.py, metadata.py — tested, working

\- Retrieval (Aayush): embeddings.py, vector\_store.py, retriever.py — tested, working

\- Both branches merged into main

\- Full integration test passing: 941 real EV chunks indexed, 3 test queries

&#x20; returned highly relevant results (best: 0.41 distance on a specific technical query)

\- Knowledge base: 3 EV documents (arXiv x2, IEA Global EV Outlook 2024)



\## Next Steps

\- \[ ] Add more EV documents (target 15-25 total, currently have 3)

\- \[ ] Start Week 2: LangGraph agent state + Planner + Router nodes



\## Week 2 — COMPLETE ✅

\- state.py: shared ResearchState model

\- planner.py: breaks query into sub-questions, flags freshness need (Gemini 3.6 Flash)

\- router.py: decides local/web/both/clarify routing (Aayush)

\- rag\_tool.py, web\_search.py: tool wrappers, Tavily excludes reddit/quora/pinterest (Aayush)

\- graph.py: LangGraph wiring Planner -> Router -> END

\- Verified end-to-end: compound query correctly split, routed to "both" with clear reasoning



\## Next Steps

\- \[ ] Week 3: wire Retriever into the graph (calls rag\_tool/web\_search based on route\_decision)

\- \[ ] Week 3: build Grader (evaluates evidence quality)

\- \[ ] Week 3: build Rewriter + retry loop

\- \[ ] Week 3: build Synthesizer + Report Compiler



\## Week 3 — CORE COMPLETE ✅

\- retriever\_node.py, grader.py: wired into graph

\- rewriter.py, synthesizer.py, report\_compiler.py: complete

\- Switched LLM provider Gemini -> Groq (openai/gpt-oss-120b) due to Gemini free-tier daily limit

\- Full graph verified: real query -> retry loop -> cited report generated

\- Known issue: grade scores low (0.1-0.2) due to thin corpus (3 docs) — expect improvement once more EV docs added



\## Next Steps

\- \[ ] Add more EV documents (target 15-25)

\- \[ ] Week 4: Streamlit UI, FastAPI backend, Docker

\- \[ ] Week 4: baseline RAG comparison, evaluation metrics

