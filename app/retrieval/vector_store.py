"""
Vector store setup using ChromaDB.
Stores embedded chunks and allows similarity search over them.
"""

import os
import chromadb

# ChromaDB persists to disk here — matches the data/chroma/ folder
# already set up in the project structure (gitignored, local only).
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_CHROMA_PATH = os.path.join(_PROJECT_ROOT, "data", "chroma")

_client = None
_collection = None


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=_CHROMA_PATH)
    return _client


def get_collection(name: str = "ev_research"):
    """
    Get (or create) the ChromaDB collection where all chunks live.
    """
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(name=name)
    return _collection


def add_chunks_to_store(embedded_chunks: list[dict], collection_name: str = "ev_research"):
    """
    Add a list of embedded chunks (from embeddings.py) into ChromaDB.
    Each chunk must already have an 'embedding' field.
    """
    collection = get_collection(collection_name)

    ids = [c["chunk_id"] for c in embedded_chunks]
    embeddings = [c["embedding"] for c in embedded_chunks]
    documents = [c["text"] for c in embedded_chunks]

    # Metadata stored alongside each vector — everything except the
    # heavy fields (embedding, full text) which are stored separately.
    metadatas = []
    for c in embedded_chunks:
        metadatas.append({
            "source_filename": c.get("source_filename", "unknown"),
            "chunk_index": c.get("chunk_index", -1),
            "domain": c.get("domain", "unknown"),
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"Added {len(ids)} chunks to collection '{collection_name}'.")


def search_store(query_embedding: list[float], top_k: int = 5, collection_name: str = "ev_research"):
    """
    Run a similarity search against the vector store.
    Returns the top_k most similar chunks with their text + metadata.
    """
    collection = get_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    return results


if __name__ == "__main__":
    # Quick manual test with dummy data — chains embeddings.py -> vector_store.py
    from embeddings import embed_chunks, embed_text

    dummy_chunks = [
        {"chunk_id": "test_1", "source_filename": "dummy.pdf", "chunk_index": 0,
         "domain": "EV Technology", "text": "Electric vehicles use lithium-ion batteries for energy storage."},
        {"chunk_id": "test_2", "source_filename": "dummy.pdf", "chunk_index": 1,
         "domain": "EV Technology", "text": "Charging infrastructure is critical for EV adoption."},
        {"chunk_id": "test_3", "source_filename": "dummy.pdf", "chunk_index": 2,
         "domain": "EV Technology", "text": "Battery degradation affects EV range over time."},
    ]

    embedded = embed_chunks(dummy_chunks)
    add_chunks_to_store(embedded)

    query_vector = embed_text("How does battery health change with use?")
    results = search_store(query_vector, top_k=2)

    print("\nQuery: 'How does battery health change with use?'")
    print("Top results:")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f"  - ({dist:.4f}) {doc}")