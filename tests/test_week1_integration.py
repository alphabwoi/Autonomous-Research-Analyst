"""
Full Week 1 integration test — real pipeline, no dummy data.

Chains: loaders.py -> chunker.py -> metadata.py (ingestion)
     -> embeddings.py -> vector_store.py (retrieval)

Run this from the project root: python tests/test_week1_integration.py
"""

import os
import sys

# Make sure both app/ingestion and app/retrieval are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app", "ingestion"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app", "retrieval"))

from loaders import load_all_pdfs
from chunker import chunk_all_documents
from metadata import enrich_all_chunks
from retriever import index_chunks, retrieve


def run_integration_test():
    raw_data_path = os.path.join(PROJECT_ROOT, "data", "raw")

    print("=" * 60)
    print("STEP 1: Loading PDFs")
    print("=" * 60)
    docs = load_all_pdfs(raw_data_path)

    print("\n" + "=" * 60)
    print("STEP 2: Chunking")
    print("=" * 60)
    chunks = chunk_all_documents(docs)

    print("\n" + "=" * 60)
    print("STEP 3: Enriching metadata")
    print("=" * 60)
    enriched_chunks = enrich_all_chunks(chunks)
    print(f"Enriched {len(enriched_chunks)} chunks.")

    print("\n" + "=" * 60)
    print("STEP 4: Embedding + indexing into ChromaDB")
    print("=" * 60)
    print("(This may take a few minutes for ~940 chunks — be patient.)")
    index_chunks(enriched_chunks, collection_name="ev_research")

    print("\n" + "=" * 60)
    print("STEP 5: Test retrieval with real EV queries")
    print("=" * 60)

    test_queries = [
        "What are the main challenges in EV battery degradation?",
        "How does EV charging infrastructure affect adoption?",
        "What ultrasonic methods are used to monitor lithium-ion batteries?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retrieve(query, top_k=3, collection_name="ev_research")
        for r in results:
            print(f"  - ({r['similarity_distance']:.4f}) [{r['source_filename']}] {r['text'][:150]}...")

    print("\n" + "=" * 60)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_integration_test()
