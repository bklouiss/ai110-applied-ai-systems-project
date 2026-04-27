"""
rag/retriever.py
----------------
Top-level retrieval interface used by the Research Agent. Combines the Embedder
and VectorStore to accept a raw query string and return a ranked list of Passage
objects with content, source attribution, and similarity scores. This is the only
RAG component the Research Agent needs to interact with directly.
"""

from models import Passage
from rag.embedder import Embedder
from rag.vector_store import VectorStore


class Retriever:

    def __init__(self):
        """
        Instantiates the Embedder and VectorStore. The ChromaDB collection must
        already exist (built via build_index.py) before retrieve() is called.
        Raises if the collection is not found.
        """
        self.embedder = Embedder()
        self.store = VectorStore()

    def retrieve(self, query: str, k: int = 3) -> list[Passage]:
        """
        Embeds the query string, queries ChromaDB for the k nearest neighbors by
        cosine similarity, and returns the results as a sorted list of Passage objects.

        Converts ChromaDB cosine distances to similarity scores by computing
        1 - distance, so higher scores indicate greater relevance.

        Args:
            query: Raw user query string to embed and search against.
            k: Number of passages to retrieve. Defaults to 3.

        Returns:
            List of Passage objects sorted by similarity score descending, each
            carrying content, source filename, and similarity score.
        """
        embedding = self.embedder.embed(query)
        results = self.store.query(embedding, k)

        passages = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            passages.append(Passage(
                content=doc,
                source=meta["source"],
                score=round(1 - dist, 4),
            ))

        return sorted(passages, key=lambda p: p.score, reverse=True)
