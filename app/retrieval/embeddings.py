"""
Embedding generation for the retrieval pipeline.
Uses a local sentence-transformers model (free, no API cost).
"""

from sentence_transformers import SentenceTransformer

# Small, fast, good-quality model — 384-dim embeddings.
# Downloads automatically the first time this runs (~80MB).
_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def get_model() -> SentenceTransformer:
    """
    Lazy-load the embedding model so it's only downloaded/loaded once,
    not every time this module is imported.
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {_MODEL_NAME} (first run downloads it)...")
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """
    Embed a single string. Returns a list of floats (the vector).
    """
    model = get_model()
    vector = model.encode(text)
    return vector.tolist()


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed a list of chunk dicts (from metadata.py / chunker.py).
    Adds an 'embedding' field to each chunk, returns the updated list.

    Batched for speed — much faster than embedding one at a time.
    """
    model = get_model()
    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    vectors = model.encode(texts, show_progress_bar=True)

    enriched = []
    for chunk, vector in zip(chunks, vectors):
        chunk_with_embedding = dict(chunk)
        chunk_with_embedding["embedding"] = vector.tolist()
        enriched.append(chunk_with_embedding)

    return enriched


if __name__ == "__main__":
    # Quick manual test with dummy data — doesn't require Mohit's
    # real PDFs/chunks, so you can test this file standalone.
    dummy_chunks = [
        {"chunk_id": "test_1", "text": "Electric vehicles use lithium-ion batteries for energy storage."},
        {"chunk_id": "test_2", "text": "Charging infrastructure is critical for EV adoption."},
        {"chunk_id": "test_3", "text": "Battery degradation affects EV range over time."},
    ]

    result = embed_chunks(dummy_chunks)
    print(f"\nEmbedded {len(result)} chunks.")
    print(f"Embedding dimension: {len(result[0]['embedding'])}")
    print(f"Sample embedding (first 5 values): {result[0]['embedding'][:5]}")