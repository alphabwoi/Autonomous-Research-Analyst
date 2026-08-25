"""
Retriever — the clean public interface for the retrieval system.
Combines embeddings.py + vector_store.py into simple functions that
the rest of the app (agent nodes, tools) can call without knowing
about embedding models or ChromaDB internals.
"""

from embeddings import embed_text, embed_chunks
from vector_store import add_chunks_to_store, search_store


def index_chunks(chunks: list[dict], collection_name: str = "ev_research"):
    """
    Full indexing pipeline: takes raw chunks (from Mohit's ingestion
    pipeline: loaders.py -> chunker.py -> metadata.py), embeds them,
    and stores them in ChromaDB.

    Call this once per new batch of documents.
    """
    embedded_chunks = embed_chunks(chunks)
    add_chunks_to_store(embedded_chunks, collection_name=collection_name)
    print(f"Indexed {len(chunks)} chunks into '{collection_name}'.")


def retrieve(query: str, top_k: int = 5, collection_name: str = "ev_research") -> list[dict]:
    """
    The main retrieval function. Given a natural-language query,
    returns the top_k most relevant chunks with their text + metadata.

    This is the function the agent's Retriever node will call.
    """
    query_vector = embed_text(query)
    raw_results = search_store(query_vector, top_k=top_k, collection_name=collection_name)

    # Reshape ChromaDB's raw output into a clean list of dicts —
    # easier for the rest of the app (grader, synthesizer) to work with.
    results = []
    documents = raw_results["documents"][0]
    metadatas = raw_results["metadatas"][0]
    distances = raw_results["distances"][0]
    ids = raw_results["ids"][0]

    for doc_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
        results.append({
            "chunk_id": doc_id,
            "text": text,
            "source_filename": metadata.get("source_filename", "unknown"),
            "domain": metadata.get("domain", "unknown"),
            "similarity_distance": distance,
        })

    return results


if __name__ == "__main__":
    # Quick manual test — index dummy chunks, then retrieve.
    dummy_chunks = [
        {"chunk_id": "test_1", "source_filename": "dummy.pdf", "chunk_index": 0,
         "domain": "EV Technology", "text": "Electric vehicles use lithium-ion batteries for energy storage."},
        {"chunk_id": "test_2", "source_filename": "dummy.pdf", "chunk_index": 1,
         "domain": "EV Technology", "text": "Charging infrastructure is critical for EV adoption."},
        {"chunk_id": "test_3", "source_filename": "dummy.pdf", "chunk_index": 2,
         "domain": "EV Technology", "text": "Battery degradation affects EV range over time."},
    ]

    index_chunks(dummy_chunks)

    results = retrieve("How does battery health change with use?", top_k=2)

    print("\nQuery: 'How does battery health change with use?'")
    print("Top results:")
    for r in results:
        print(f"  - ({r['similarity_distance']:.4f}) {r['text']}")