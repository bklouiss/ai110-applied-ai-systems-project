# AlgoAssist — System Design Document

## Overview

AlgoAssist is a multi-agent RAG system that helps programmers research algorithms, design patterns, and CS concepts. It retrieves relevant knowledge, generates grounded code, and explains every decision in plain language. The system is designed to teach, not just produce — every AI output is traceable to a citable source.

---

## Operating Modes

| Mode | Name | Description |
|------|------|-------------|
| 0 | Standard IDE | No AI assistance — conceptual baseline for comparison only, not selectable in app |
| 1 | Naive LLM | Query sent directly to Claude with no retrieval |
| 2 | RAG + Article | Retrieves relevant passages and generates a GeeksforGeeks-style educational article with code examples, complexity analysis, and practical guidance |
| 3 | RAG + Code | Retrieves context, generates grounded code with source citations |
| 4 | Full Agentic | Orchestrator sequences Research → Code → Explainer agents |

Mode 0 is a conceptual reference point used in evaluation and presentation (Option B: pre-run sample queries across modes). Modes 1–4 are selectable in the app. Mode 4 is the primary mode.

---

## System Architecture

```
User Query (query: str, mode: int)
    |
    v
[Entry Point: app.py (Streamlit) | main.py (CLI)]
    |
    v
[Mode Router]
    |
    |-- Mode 1 --> [Claude API] -----------------------> NaiveResponse
    |
    |-- Mode 2 --> [Research Agent] --> [Article Agent] -> ArticleResult
    |                    |
    |              [ChromaDB + Embedder]
    |
    |-- Mode 3 --> [Research Agent] --> [Code Agent] -> CodeResult
    |                    |
    |              [ChromaDB + Embedder]
    |
    |-- Mode 4 --> [Orchestrator]
                        |
                        v
                  [Research Agent] <--> [ChromaDB + Embedder]
                     |        |
                     |     passages
                     |        |
                     v        v
                [Code Agent]  |
                     |        |
                  CodeResult  |
                     |        |
                     v        v
                [Explainer Agent]
                        |
                        v
                  AgenticResponse
```

---

## Data Shapes

### Entry — Query Request

```python
@dataclass
class QueryRequest:
    query: str
    mode: int  # 1–4
```

---

### Research Agent

```python
# Input
@dataclass
class ResearchInput:
    query: str

# Output
@dataclass
class Passage:
    content: str
    source: str    # filename from knowledge_base/docs/
    score: float   # cosine similarity score from ChromaDB

@dataclass
class ResearchResult:
    query: str
    passages: list[Passage]
```

---

### Code Agent

```python
# Input
@dataclass
class CodeInput:
    query: str
    passages: list[Passage]

# Output
@dataclass
class CodeResult:
    code: str
    language: str      # "python" for v1
    sources: list[str] # source filenames cited in generation
```

---

### Explainer Agent

```python
# Input
@dataclass
class ExplainerInput:
    query: str
    code: str
    passages: list[Passage]

# Output
@dataclass
class ExplainerResult:
    explanation: str
    sources: list[str]
```

---

### Orchestrator (Mode 4)

```python
# Input
QueryRequest  # mode must be 4

# Output
@dataclass
class AgenticResponse:
    query: str
    mode: int
    passages: list[Passage]
    code: CodeResult
    explanation: ExplainerResult
```

---

### Mode 1 Response

```python
@dataclass
class NaiveResponse:
    query: str
    response: str  # raw Claude output, no retrieval context
```

---

## RAG Pipeline

### Embedder — `rag/embedder.py`
- Model: `all-MiniLM-L6-v2` (sentence-transformers, runs locally)
- Used at index time (documents) and query time (one embedding per query)

### Vector Store — `rag/vector_store.py`
- Backend: ChromaDB (local persistence, no external server)
- Operations: `index`, `query`, `persist`
- Single collection with source metadata for filtering

### Retriever — `rag/retriever.py`
- Returns top-k passages ranked by cosine similarity
- Attaches `source` (filename) and `score` to each `Passage`
- Default k: 3

---

## Knowledge Base

Located in `knowledge_base/docs/`. Markdown files embedded once via `build_index.py` and persisted in ChromaDB. Re-run `build_index.py` only when documents are added or changed.

| Category | Files |
|----------|-------|
| Algorithms | `binary_search.md`, `sorting_algorithms.md`, `graph_traversal.md`, `dynamic_programming.md` |
| Concepts | `complexity_guide.md` |
| Design Patterns | `design_patterns/` (subdirectory) |

---

## Agents Module

| File | Agent | Role |
|------|-------|------|
| `agents/orchestrator.py` | Orchestrator | Sequences Research → Code → Explainer for Mode 4; assembles AgenticResponse |
| `agents/research_agent.py` | Research Agent | Embeds query and retrieves top-k passages from ChromaDB; used in Modes 2–4 |
| `agents/article_agent.py` | Article Agent | Generates a GeeksforGeeks-style educational article from retrieved passages; Mode 2 |
| `agents/code_agent.py` | Code Agent | Generates grounded Python code via Claude API using query and passages; Modes 3–4 |
| `agents/explainer_agent.py` | Explainer Agent | Produces plain-language breakdown of generated code via Claude API; Mode 4 only |

---

## Entry Points

| File | Purpose |
|------|---------|
| `models.py` | Shared dataclasses — input/output contracts for all agents and pipeline stages |
| `app.py` | Streamlit UI — mode selector, query input, formatted response display |
| `main.py` | CLI — accepts query and mode as arguments or interactive prompt |
| `build_index.py` | One-time indexing script — embeds all docs and persists ChromaDB collection |
