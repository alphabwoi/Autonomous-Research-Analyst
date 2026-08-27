"""
FastAPI backend — exposes the agent graph (and baseline) as HTTP endpoints.
Run with: uvicorn app.main:app --reload
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "agents"))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "evaluation"))

from fastapi import FastAPI
from pydantic import BaseModel

from graph import run_query
from baseline_rag import run_baseline

app = FastAPI(title="Autonomous Research Analyst API")


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/research")
def research(request: QueryRequest):
    """
    Runs the full agentic pipeline: Planner -> Router -> Retriever ->
    Grader -> Rewriter (retry loop) -> Synthesizer -> Report Compiler.
    """
    result = run_query(request.query)
    return {
        "query": request.query,
        "report": result.get("final_report", ""),
        "retry_count": result.get("retry_count", 0),
        "route_decision": result.get("route_decision", ""),
        "grade_score": result.get("grade_score"),
    }


@app.post("/baseline")
def baseline(request: QueryRequest):
    """
    Runs the simple baseline RAG pipeline (no agent loop) for comparison.
    """
    result = run_baseline(request.query)
    return {
        "query": request.query,
        "answer": result.get("answer", ""),
        "chunks_used": result.get("chunks_used", 0),
    }