"""
Chunking logic for the ingestion pipeline.
Splits long document text into smaller overlapping chunks suitable
for embedding + retrieval.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(document: dict, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Split a single loaded document (from loaders.py) into chunks.

    chunk_size / chunk_overlap are in characters, not tokens — good enough
    approximation for now. ~1000 chars ≈ 200-250 tokens.

    Returns a list of chunk dicts, each carrying a reference back to
    the source document so metadata.py can attach full provenance later.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(document["text"])

    chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "chunk_id": f"{document['filename']}_chunk{i}",
            "text": chunk_text,
            "source_filename": document["filename"],
            "source_path": document["source_path"],
            "chunk_index": i,
        })

    return chunks


def chunk_all_documents(documents: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Chunk a list of loaded documents (from load_all_pdfs) into one flat
    list of chunks, ready for embedding.
    """
    all_chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc, chunk_size, chunk_overlap)
        all_chunks.extend(doc_chunks)
        print(f"{doc['filename']}: {len(doc_chunks)} chunks")

    return all_chunks


if __name__ == "__main__":
    # Quick manual test — chains loaders.py output into chunker.py
    import os
    from loaders import load_all_pdfs

    # Resolve data/raw relative to the project root, regardless of
    # which folder this script is run from.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_data_path = os.path.join(project_root, "data", "raw")

    docs = load_all_pdfs(raw_data_path)
    chunks = chunk_all_documents(docs)

    print(f"\nTotal chunks created: {len(chunks)}")
    if chunks:
        print(f"\nSample chunk:\n{chunks[0]}")