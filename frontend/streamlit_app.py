"""
Streamlit UI — talks to the FastAPI backend (app/main.py) to run
research queries and display results.

Run with: streamlit run frontend/streamlit_app.py
Requires the FastAPI server running separately: uvicorn app.main:app --reload
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Autonomous Research Analyst", page_icon="🔋", layout="centered")

st.title("🔋 Autonomous Research Analyst")
st.caption("EV Technology research assistant — agentic RAG pipeline")

mode = st.radio("Mode", ["Agentic Pipeline", "Baseline RAG"], horizontal=True)

query = st.text_area("Ask a research question", placeholder="e.g. What are the main challenges in EV battery degradation?", height=100)

if st.button("Run Research", type="primary"):
    if not query.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Researching... this may take a minute."):
            try:
                if mode == "Agentic Pipeline":
                    response = requests.post(f"{API_URL}/research", json={"query": query}, timeout=180)
                else:
                    response = requests.post(f"{API_URL}/baseline", json={"query": query}, timeout=180)

                response.raise_for_status()
                data = response.json()

                if mode == "Agentic Pipeline":
                    st.subheader("Report")
                    st.markdown(data.get("report", "No report generated."))

                    with st.expander("Pipeline details"):
                        st.write(f"**Route decision:** {data.get('route_decision', 'N/A')}")
                        st.write(f"**Retries used:** {data.get('retry_count', 0)}")
                        st.write(f"**Final grade score:** {data.get('grade_score', 'N/A')}")
                else:
                    st.subheader("Answer")
                    st.markdown(data.get("answer", "No answer generated."))
                    st.caption(f"Chunks used: {data.get('chunks_used', 0)}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Make sure the FastAPI server is running: `uvicorn app.main:app --reload`")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.caption("Domain: EV Technology | Powered by Groq + LangGraph + ChromaDB")