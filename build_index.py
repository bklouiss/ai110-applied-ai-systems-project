"""
build_index.py
--------------
One-time script that reads all Markdown files from knowledge_base/docs/,
splits them into overlapping passages, embeds each passage using
sentence-transformers (all-MiniLM-L6-v2), and persists the embeddings to
ChromaDB. Run this script once before starting the application, and re-run
it whenever knowledge base documents are added or updated. Does not require
an Anthropic API key.

Usage:
    python build_index.py
"""

import os
from pathlib import Path
from rag.embedder import Embedder
from rag.vector_store import VectorStore


def load_documents(docs_dir: str = "knowledge_base/docs") -> list[dict]:
    """
    Recursively reads all .md files from the docs directory tree. Each file
    is returned as a single document dict. Subdirectories (e.g., design_patterns/)
    are traversed automatically.

    Args:
        docs_dir: Path to the root directory containing knowledge base Markdown files.

    Returns:
        List of dicts, each with:
            'content' (str): Full text content of the file.
            'source'  (str): Filename relative to docs_dir (e.g., 'binary_search.md').
    """
    documents = []
    docs_path = Path(docs_dir)
    for md_file in sorted(docs_path.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        source = str(md_file.relative_to(docs_path)).replace("\\", "/")
        documents.append({"content": content, "source": source})
    return documents


def split_passages(document: dict, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Splits a document's content into overlapping fixed-size character chunks.
    Overlap ensures that context at chunk boundaries is not lost when a passage
    is retrieved in isolation.

    Args:
        document:   Dict with 'content' and 'source' keys.
        chunk_size: Maximum character length per passage chunk. Defaults to 500.
        overlap:    Number of characters to repeat at the start of each new chunk
                    from the end of the previous one. Defaults to 50.

    Returns:
        List of passage dicts, each with 'content' and 'source' keys.
    """
    content = document["content"]
    source = document["source"]
    passages = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk = content[start:end]
        if chunk.strip():
            passages.append({"content": chunk, "source": source})
        if end == len(content):
            break
        start = end - overlap
    return passages


def build_index() -> None:
    """
    Orchestrates the full indexing pipeline:
        1. Loads all Markdown documents from knowledge_base/docs/.
        2. Splits each document into overlapping passages.
        3. Embeds all passages in a single batch using sentence-transformers.
        4. Indexes the passages and their embeddings into ChromaDB.

    Prints progress to stdout at each stage. Safe to re-run — existing entries
    with matching document IDs are overwritten rather than duplicated.
    """
    print("Loading documents...")
    documents = load_documents()
    print(f"  {len(documents)} documents loaded")

    print("Splitting into passages...")
    all_passages = []
    for doc in documents:
        all_passages.extend(split_passages(doc))
    print(f"  {len(all_passages)} passages created")

    print("Embedding passages (this may take a moment)...")
    embedder = Embedder()
    texts = [p["content"] for p in all_passages]
    sources = [p["source"] for p in all_passages]
    embeddings = embedder.embed_batch(texts)
    print(f"  {len(embeddings)} embeddings generated")

    print("Indexing into ChromaDB...")
    store = VectorStore()
    store.index(texts, sources, embeddings)
    print(f"  {len(texts)} passages indexed")
    print("Done. Index is ready.")


if __name__ == "__main__":
    build_index()
