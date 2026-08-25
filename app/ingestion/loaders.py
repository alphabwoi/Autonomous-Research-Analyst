"""
Document loaders for the ingestion pipeline.
Currently supports PDF files. Extend with more loader functions
(e.g. load_web_document, load_docx) as new sources are added.
"""

import os
from pypdf import PdfReader


def load_pdf(file_path: str) -> dict:
    """
    Load a single PDF and extract its raw text.
    Returns a dict with the file path, extracted text, and page count.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return {
        "source_path": file_path,
        "filename": os.path.basename(file_path),
        "text": text.strip(),
        "num_pages": len(reader.pages),
    }


def load_all_pdfs(folder_path: str) -> list[dict]:
    """
    Load every PDF in a folder (non-recursive).
    Returns a list of document dicts (see load_pdf).
    """
    documents = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            try:
                doc = load_pdf(full_path)
                documents.append(doc)
                print(f"Loaded: {filename} ({doc['num_pages']} pages)")
            except Exception as e:
                print(f"WARNING: failed to load {filename}: {e}")

    return documents


if __name__ == "__main__":
    docs = load_all_pdfs("data/raw")
    print(f"\nTotal documents loaded: {len(docs)}")
    if docs:
        print(f"Preview of first doc text:\n{docs[0]['text'][:300]}")