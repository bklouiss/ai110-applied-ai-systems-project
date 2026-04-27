"""
rag/__init__.py
---------------
Package initializer for the rag module. Exposes the three RAG pipeline
components at the package level for convenient importing throughout the
application.
"""

from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever

__all__ = ["Embedder", "VectorStore", "Retriever"]
