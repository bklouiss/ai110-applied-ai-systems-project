"""
rag/vector_store.py
-------------------
ChromaDB interface for storing and querying document embeddings. Manages a single
persistent collection backed by local disk storage — no external server required.
Provides index and query operations used by build_index.py and retriever.py
respectively. The collection persists across runs; re-indexing overwrites existing
entries by document ID.
"""

import chromadb


class VectorStore:

    def __init__(self, persist_directory: str = ".chromadb"):
        """
        Initializes the ChromaDB persistent client and creates or loads the
        existing collection named 'knowledge_base'. The collection uses cosine
        similarity as its distance metric.

        Args:
            persist_directory: Path to the directory where ChromaDB stores its
                               data files. Defaults to .chromadb in the project root.
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )

    def index(self, texts: list[str], sources: list[str], embeddings: list[list[float]]) -> None:
        """
        Adds documents to the ChromaDB collection with their pre-computed embeddings
        and source metadata. Generates stable document IDs from the source filename
        and passage index to ensure idempotent re-indexing — re-running build_index.py
        overwrites existing entries rather than creating duplicates.

        Args:
            texts: List of passage content strings to store.
            sources: List of source filenames corresponding to each passage.
            embeddings: Pre-computed embedding vectors for each passage, in the
                        same order as texts and sources.
        """
        source_counts: dict[str, int] = {}
        ids = []
        for source in sources:
            idx = source_counts.get(source, 0)
            source_counts[source] = idx + 1
            safe = source.replace("/", "_").replace("\\", "_").replace(".", "_").replace(" ", "_")
            ids.append(f"{safe}_{idx}")

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=[{"source": s} for s in sources],
        )

    def query(self, embedding: list[float], k: int = 3) -> dict:
        """
        Queries the collection for the k passages most similar to the given
        embedding using cosine similarity.

        Args:
            embedding: Query embedding vector produced by Embedder.embed().
            k: Number of top results to return. Defaults to 3.

        Returns:
            ChromaDB results dict with keys: 'documents', 'metadatas', 'distances'.
            distances are cosine distances (0 = identical, 2 = opposite).
        """
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
