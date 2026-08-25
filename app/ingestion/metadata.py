"""
Metadata enrichment for the ingestion pipeline.
Takes chunks (from chunker.py) and attaches additional metadata
useful for citations and filtering later (title, ingestion date, etc.)
"""

import os
import hashlib
from datetime import datetime, timezone


def enrich_chunk_metadata(chunk: dict, domain: str = "EV Technology") -> dict:
    """
    Add extra metadata fields to a single chunk dict (from chunker.py).
    Does not overwrite existing fields — only adds new ones.
    """
    enriched = dict(chunk)  # copy, don't mutate the original

    enriched["domain"] = domain
    enriched["ingested_at"] = datetime.now(timezone.utc).isoformat()

    # Simple checksum of the chunk text — useful later for detecting
    # duplicate/near-duplicate chunks across documents.
    enriched["content_hash"] = hashlib.md5(chunk["text"].encode("utf-8")).hexdigest()[:12]

    # Derive a readable title guess from filename (strip extension,
    # replace underscores). Good enough placeholder until real
    # titles are extracted from PDF metadata/first page.
    name_without_ext = os.path.splitext(chunk["source_filename"])[0]
    enriched["title_guess"] = name_without_ext.replace("_", " ").replace("-", " ")

    # Short preview, useful for debugging/logging without printing
    # the full chunk text.
    enriched["preview"] = chunk["text"][:120].replace("\n", " ") + "..."

    return enriched


def enrich_all_chunks(chunks: list[dict], domain: str = "EV Technology") -> list[dict]:
    """
    Apply enrich_chunk_metadata to a full list of chunks.
    """
    return [enrich_chunk_metadata(c, domain) for c in chunks]


if __name__ == "__main__":
    # Quick manual test — chains loaders.py -> chunker.py -> metadata.py
    import os
    from loaders import load_all_pdfs
    from chunker import chunk_all_documents

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_data_path = os.path.join(project_root, "data", "raw")

    docs = load_all_pdfs(raw_data_path)
    chunks = chunk_all_documents(docs)
    enriched_chunks = enrich_all_chunks(chunks)

    print(f"\nTotal enriched chunks: {len(enriched_chunks)}")
    if enriched_chunks:
        print(f"\nSample enriched chunk:\n{enriched_chunks[0]}")