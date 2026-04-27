"""
models.py
---------
Shared dataclasses defining the input/output contracts for all agents and
pipeline stages in AlgoAssist. Every agent imports from this module to ensure
consistent data shapes across the system. These types map directly to the
data shapes documented in assets/design_doc.md.
"""

from dataclasses import dataclass


@dataclass
class QueryRequest:
    """
    Top-level entry point for all queries. Carries the user's natural-language
    query and the selected operating mode (1–4). Created by app.py or main.py
    and passed to the appropriate agent or the Orchestrator.
    """
    query: str
    mode: int  # 1–4


@dataclass
class Passage:
    """
    A single retrieved passage from the knowledge base. Produced by the
    Retriever and consumed by the Research Agent, Code Agent, and Explainer Agent.
    Carries the passage text, the source filename it came from, and its cosine
    similarity score relative to the query.
    """
    content: str
    source: str   # filename relative to knowledge_base/docs/
    score: float  # cosine similarity score from ChromaDB (higher = more relevant)


@dataclass
class ResearchInput:
    """
    Input contract for the Research Agent. Wraps the raw user query string
    before it is embedded and used to query ChromaDB.
    """
    query: str


@dataclass
class ResearchResult:
    """
    Output from the Research Agent. Contains the original query for traceability
    and the list of top-k Passage objects ranked by cosine similarity.
    """
    query: str
    passages: list[Passage]


@dataclass
class CodeInput:
    """
    Input contract for the Code Agent. Pairs the user query with the retrieved
    passages so the agent can construct a retrieval-grounded prompt for Claude.
    """
    query: str
    passages: list[Passage]


@dataclass
class CodeResult:
    """
    Output from the Code Agent. Contains the generated code string, a language
    tag (always "python" for v1), and the list of source filenames that were
    cited in the generation prompt.
    """
    code: str
    language: str       # "python" for v1
    sources: list[str]  # source filenames cited in the generation prompt


@dataclass
class ExplainerInput:
    """
    Input contract for the Explainer Agent. Provides the query for context,
    the generated code to be explained, and the original retrieved passages
    so the explanation can reference source material.
    """
    query: str
    code: str
    passages: list[Passage]


@dataclass
class ExplainerResult:
    """
    Output from the Explainer Agent. Contains a plain-language step-by-step
    breakdown of the generated code and the source filenames referenced in
    the explanation.
    """
    explanation: str
    sources: list[str]


@dataclass
class AgenticResponse:
    """
    Full Mode 4 response combining all agent outputs. Assembled by the
    Orchestrator after all three agents have run. Contains the retrieved
    passages, the generated code result, and the plain-language explanation.
    """
    query: str
    mode: int
    passages: list[Passage]
    code: CodeResult
    explanation: ExplainerResult


@dataclass
class ArticleResult:
    """
    Mode 2 response. A GeeksforGeeks-style educational article generated from
    retrieved knowledge base passages. Contains a structured markdown article
    covering introduction, algorithm walkthrough, Python implementation,
    complexity analysis, worked example, and practical guidance.
    """
    query: str
    title: str
    content: str    # full article in markdown
    sources: list[str]


@dataclass
class NaiveResponse:
    """
    Mode 1 response. Contains the raw Claude API output with no retrieval
    context. Used as a baseline comparison against grounded modes.
    """
    query: str
    response: str
