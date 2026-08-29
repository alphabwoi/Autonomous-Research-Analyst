# Autonomous Research Analyst

An agentic RAG (Retrieval-Augmented Generation) system that plans, routes,
retrieves, self-grades its own evidence, retries on poor evidence, and
synthesizes a cited report — built for the EV Technology domain.

Unlike a simple RAG pipeline that retrieves once and answers regardless of
evidence quality, this system checks its own work: a **Grader** node scores
retrieved evidence, and if the score is too low, a **Rewriter** node
reformulates the query and tries again (up to 2 retries) before writing the
final answer.

## Quick Links

- [Setup Guide](docs/setup.md) — get the project running locally
- [User Guide](docs/user-guide.md) — how to use the app
- [Developer Guide](docs/developer-guide.md) — how the codebase is organized
- [Architecture / Full Documentation](PROJECT_DOCUMENTATION.md) — deep technical walkthrough
- [Evaluation Results](docs/evaluation.md) — baseline vs. agentic comparison

## Architecture (at a glance)

```
Query → Planner → Router → Retriever → Grader → (retry loop) → Synthesizer → Report
```

- **Planner** — breaks the question into sub-questions, flags if it needs current info
- **Router** — decides: local documents, live web search, both, or clarify
- **Retriever** — pulls evidence from a local vector database (ChromaDB) and/or Tavily web search
- **Grader** — scores evidence quality (0.0–1.0); below threshold triggers a retry
- **Rewriter** — reformulates the query, loops back to the Retriever (max 2 retries)
- **Synthesizer** — writes a structured, cited answer using only the retrieved evidence
- **Report Compiler** — formats the final report with sub-questions and sources

Full explanation of every component: see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).

## Tech Stack

- **Orchestration:** LangGraph
- **LLM:** Groq (`openai/gpt-oss-120b`)
- **Vector DB:** ChromaDB (local)
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`, local, free)
- **Web search:** Tavily (excludes Reddit/Quora/Pinterest)
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Containerization:** Docker + Docker Compose

## Getting Started

See [docs/setup.md](docs/setup.md) for full installation steps. Quick version:

```bash
git clone https://github.com/alphabwoi/Autonomous-Research-Analyst.git
cd Autonomous-Research-Analyst
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in your API keys
```

Run the backend:
```bash
uvicorn app.main:app --reload
```

Run the UI (separate terminal):
```bash
streamlit run frontend/streamlit_app.py
```

Or run both via Docker:
```bash
docker compose up --build
```

## Evaluation Summary

The agentic pipeline is ~8.2x slower than a simple baseline RAG pipeline
(39s vs. 4.8s average), in exchange for: self-graded evidence (67% pass
rate), automatic retry on weak evidence, multi-source sub-question
retrieval, and explicit reporting of what the evidence does *not* cover.
Retrieval quality: Precision@5 = 0.80, Recall@5 = 0.875, MRR = 1.00.

Full results: [docs/evaluation.md](docs/evaluation.md)

## Project Status

Built as a college project over 4 weeks: data ingestion → agent core →
self-reflection loop → UI/API/evaluation. See [PROGRESS.md](PROGRESS.md)
for the detailed build log.

## Contributors

Built by Mohit and Aayush.