"""
agents/research_agent.py
------------------------
Research Agent responsible for RAG retrieval. Embeds the user query using
sentence-transformers, queries ChromaDB for semantically similar passages,
and returns the top-k results with source attribution and similarity scores.
Used in Modes 2, 3, and 4. Does not call the Claude API.
"""

from models import ResearchInput, ResearchResult
from rag.retriever import Retriever


class ResearchAgent:

    def __init__(self):
        """
        Instantiates the Retriever, which in turn loads the sentence-transformers
        embedding model and opens the ChromaDB collection. The ChromaDB index must
        exist before this agent is used (built via build_index.py).
        """
        self.retriever = Retriever()

    def run(self, research_input: ResearchInput) -> ResearchResult:
        """
        Embeds the query string and retrieves the top-k most semantically similar
        passages from the ChromaDB knowledge base.

        Args:
            research_input: ResearchInput containing the user's raw query string.

        Returns:
            ResearchResult with the original query and a list of Passage objects,
            each carrying content, source filename, and cosine similarity score,
            sorted by relevance descending.
        """
        passages = self.retriever.retrieve(research_input.query)
        return ResearchResult(query=research_input.query, passages=passages)
