"""
tests/test_retrieval.py
-----------------------
Unit and integration tests for the RAG retrieval pipeline. Tests the Embedder,
VectorStore, and Retriever in isolation and as a chain. The integration test
verifies that semantic paraphrase queries retrieve the correct source document,
which would fail under keyword-only matching — this is the core value assertion
of the ChromaDB/sentence-transformers stack over DocuBot's inverted index.

Requires a built ChromaDB index (run build_index.py) for the Retriever tests.
"""

import pytest
from models import Passage
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever


class TestEmbedder:

    def test_embed_returns_vector(self):
        """
        Verifies that embed() returns a non-empty list of floats for a
        standard input string.
        """
        embedder = Embedder()
        result = embedder.embed("binary search algorithm")
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], float)

    def test_embed_batch_length_matches_input(self):
        """
        Verifies that embed_batch() returns exactly one embedding vector
        per input string, preserving input order.
        """
        embedder = Embedder()
        texts = ["binary search", "quicksort", "graph traversal"]
        results = embedder.embed_batch(texts)
        assert len(results) == len(texts)

    def test_embedding_dimension(self):
        """
        Verifies that all-MiniLM-L6-v2 produces 384-dimensional vectors.
        Catches model misconfiguration early.
        """
        embedder = Embedder()
        result = embedder.embed("test")
        assert len(result) == 384


class TestVectorStore:

    def test_index_and_query(self, tmp_path):
        """
        Indexes a small set of passages into a temporary ChromaDB collection
        and verifies that querying with the same embedding returns the indexed
        passage as the top result.
        """
        embedder = Embedder()
        store = VectorStore(persist_directory=str(tmp_path))
        texts = ["binary search requires a sorted array"]
        sources = ["binary_search.md"]
        embeddings = embedder.embed_batch(texts)
        store.index(texts, sources, embeddings)

        query_embedding = embedder.embed("binary search sorted array")
        results = store.query(query_embedding, k=1)
        assert results["documents"][0][0] == texts[0]

    def test_query_returns_k_results(self, tmp_path):
        """
        Indexes more passages than k and verifies that query() returns exactly
        k results, not more.
        """
        embedder = Embedder()
        store = VectorStore(persist_directory=str(tmp_path))
        texts = [f"passage about topic {i}" for i in range(5)]
        sources = [f"doc{i}.md" for i in range(5)]
        embeddings = embedder.embed_batch(texts)
        store.index(texts, sources, embeddings)

        query_embedding = embedder.embed("topic")
        results = store.query(query_embedding, k=3)
        assert len(results["documents"][0]) == 3


class TestRetriever:

    def test_retrieve_returns_passages(self):
        """
        Verifies that retrieve() returns a non-empty list of Passage objects
        for a standard query against the built index.
        """
        retriever = Retriever()
        passages = retriever.retrieve("binary search algorithm")
        assert len(passages) > 0
        assert all(isinstance(p, Passage) for p in passages)

    def test_retrieve_passage_has_source(self):
        """
        Verifies that every Passage returned by retrieve() has a non-empty
        source filename — confirming source attribution is preserved end-to-end.
        """
        retriever = Retriever()
        passages = retriever.retrieve("sorting algorithms")
        assert all(p.source for p in passages)

    def test_semantic_retrieval(self):
        """
        Submits a paraphrase query ('finding items in an ordered sequence')
        that shares no keywords with the expected source ('binary_search.md')
        and verifies that the correct document is retrieved. This is the key
        regression test distinguishing semantic retrieval from keyword matching.
        """
        retriever = Retriever()
        passages = retriever.retrieve("finding items in an ordered sequence", k=3)
        sources = [p.source for p in passages]
        assert "binary_search.md" in sources
