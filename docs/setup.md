# Setup Guide

Step-by-step instructions to get the Autonomous Research Analyst running on
your machine.

## Prerequisites

- Python 3.11+ (developed and tested on 3.14)
- Git
- A Groq API key (free) — [console.groq.com](https://console.groq.com)
- A Tavily API key (free) — [tavily.com](https://tavily.com)
- (Optional) Docker Desktop, if you want to run via containers instead of locally

## 1. Clone the Repository

```bash
git clone https://github.com/alphabwoi/Autonomous-Research-Analyst.git
cd Autonomous-Research-Analyst
```

## 2. Create and Activate a Virtual Environment

**Windows (cmd):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You'll know it worked if your terminal prompt shows `(venv)` at the start.

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, LangGraph, ChromaDB, Streamlit, sentence-transformers,
and everything else needed. First install takes a few minutes — some
packages (like `sentence-transformers`) pull in larger ML dependencies.

## 4. Set Up API Keys

Copy the template:
```bash
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux
```

Open `.env` and fill in your keys:
```
GOOGLE_API_KEY=              (optional — legacy, project now uses Groq)
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get a Groq key at [console.groq.com](https://console.groq.com) → API Keys.
Get a Tavily key at [tavily.com](https://tavily.com) → sign up → dashboard.

**Never commit `.env` to git.** It's already excluded in `.gitignore`.

## 5. Add Source Documents

Place PDF documents into `data/raw/`. These form the local knowledge base.
The project currently uses EV Technology documents (arXiv papers, IEA
reports, industry whitepapers).

## 6. Build the Local Knowledge Base

Run the full ingestion + indexing pipeline:
```bash
python tests/test_week1_integration.py
```

This loads every PDF in `data/raw/`, splits it into chunks, embeds them, and
stores them in a local ChromaDB database at `data/chroma/`. Takes a few
minutes depending on how many documents you have.

## 7. Run the Backend

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` — you should see `{"status":"ok"}`.

## 8. Run the Frontend (separate terminal)

Activate the venv again in the new terminal, then:
```bash
streamlit run frontend/streamlit_app.py
```

This opens a browser tab at `http://localhost:8501` with the research UI.
The backend (step 7) must be running for the UI to work.

## Alternative: Run Everything via Docker

Instead of steps 7-8, you can run both backend and frontend in containers:
```bash
docker compose up --build
```
First build takes several minutes (installs all dependencies inside the
container). Subsequent runs are much faster.

## Troubleshooting

**Rate limit errors from Groq:** the free tier has request and token limits.
The system automatically retries with backoff, but very rapid repeated
testing may still hit limits — wait a minute and try again.

**`ImportError: DLL load failed` (Windows, scipy/sklearn):** usually caused
by Windows Smart App Control or antivirus blocking a DLL. Check Windows
Security → Smart App Control status, or add the `venv` folder as an
exclusion in Windows Defender.

**Empty/blank Streamlit page:** try a hard refresh (`Ctrl+F5`), a different
browser, or restart both containers/processes. Check the terminal running
Streamlit for Python errors if the page stays blank after a refresh.

**`git push` blocked for a secret:** if you accidentally commit an API key,
GitHub's push protection will block the push. Remove the secret from the
file, then either amend the commit or use `git reset --soft HEAD~1` to
undo the last commit before recommitting cleanly.
