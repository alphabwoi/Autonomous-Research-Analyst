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

