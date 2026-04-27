# AlgoAssist — Agentic RAG Coding Assistant

## Project Context (for AI assistants and collaborators)

## Video Demo Link: https://drive.google.com/file/d/1bDQEj5l1BfCPYs7txH6j9oen0nQ94YwN/view?usp=sharing

This is the final capstone project for the AI110 Applied AI Systems course. It extends **DocuBot** (Module 4 Tinker) into a multi-agent RAG system for coding assistance. The developer works between the terminal (Claude Code CLI) and VSCode (Claude Code extension). This README is the primary context file — read it in full before suggesting changes or implementations.

**Tech stack:** Python 3.11+, Anthropic Claude API, ChromaDB, sentence-transformers, Streamlit, python-dotenv, pytest  
**Entry point:** `app.py` (Streamlit UI) and `main.py` (CLI)  
**Key modules:** `agents/`, `rag/`, `knowledge_base/`, `evaluation/`  
**Environment variable required:** `ANTHROPIC_API_KEY` in `.env`

---

## Original Project: DocuBot (Module 4 Tinker)

The project this system extends is **DocuBot**, built during Module 4 of the AI110 course. DocuBot is a documentation assistant that answers developer questions about a codebase using three modes: Naive LLM (sending the full corpus to Gemini), Retrieval-Only (using a hand-built inverted index with suffix stemming), and RAG (retrieving relevant snippets before prompting Gemini). It demonstrated the core RAG pattern — retrieve first, then generate — using simple keyword overlap scoring against a small folder of Markdown documentation files.

DocuBot established the foundation this project builds on: document loading, tokenization, inverted-index retrieval, snippet selection, and LLM prompt construction. The original system's limitations (keyword-only matching, single-document queries, no agent coordination, Gemini-only integration) are the direct motivation for this upgrade.

---

## Title and Summary

**AlgoAssist** is an agentic RAG system that helps programmers research algorithms, design patterns, and CS concepts — then explains the code it generates so they understand what the AI actually built.

Most AI coding assistants are black boxes: they produce code without context, and programmers either trust it blindly or spend time reverse-engineering it. AlgoAssist takes the opposite approach. It retrieves the relevant concepts from a curated knowledge base, generates code grounded in that context, and then provides a plain-language explanation of every decision made. The result is a coding assistant that teaches rather than just completes.

**Why it matters:** Junior developers and students using AI tools risk building a dependency on code they don't understand. This system treats AI-generated code as a teaching artifact, not just an output.

---

## Architecture Overview

```
User Query
    |
    v
[Orchestrator Agent]  <-- routes query to appropriate agent(s)
    |
    |-- [Research Agent]
    |       Embeds the query using sentence-transformers
    |       Searches ChromaDB for semantically similar docs
    |       Returns top-k relevant passages with source attribution
    |
    |-- [Code Agent]
    |       Receives retrieved context + user query
    |       Calls Claude API with grounded prompt
    |       Returns code with inline comments
    |
    |-- [Explainer Agent]
            Receives generated code + source passages
            Asks Claude to produce a step-by-step plain-language breakdown
            Returns explanation keyed to specific lines/decisions

Knowledge Base (ChromaDB)
    - Algorithms (sorting, searching, graph traversal, dynamic programming)
    - Data structures (trees, heaps, hash maps, graphs)
    - Design patterns (creational, structural, behavioral)
    - CS concepts (complexity, recursion, memory management)
    - Python-specific patterns (generators, decorators, context managers)
```

The system has three operating modes (extending DocuBot's original three):

| Mode | Description |
|------|-------------|
| **1 — Naive LLM** | Query sent directly to Claude with no retrieval (baseline comparison) |
| **2 — RAG + Article** | Retrieves relevant passages and generates a GeeksforGeeks-style educational article with code, complexity analysis, and examples |
| **3 — RAG + Code** | Retrieves context, generates grounded code, cites sources |
| **4 — Full Agentic** | Orchestrator runs Research + Code + Explainer agents in sequence |

Mode 4 is the primary mode. Modes 1–3 are retained for evaluation and comparison.

---

## Setup Instructions

### 1. Clone and navigate to this directory

```bash
git clone <repo-url>
cd ai110-applied-ai-systems-project
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the environment template:

```bash
cp .env.example .env.local
```

Edit `.env.local` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 5. Build the knowledge base index

On first run, the vector index is built from the `knowledge_base/docs/` directory:

```bash
python build_index.py
```

This only needs to run once, or when you add new documents.

### 6. Run the application

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```

**CLI mode:**

CLI mode runs AlgoAssist through the terminal instead of the browser UI. It does the same thing — picks a mode, takes your query, runs the pipeline — but output is printed to stdout with section headers instead of rendered in a Streamlit UI. Useful for scripting, quick tests, or running without a browser.

Pass arguments directly:
```bash
python main.py --query "How does binary search work?" --mode 4
```

Or run with no arguments for an interactive prompt:
```bash
python main.py
```
```
Your question: How does binary search work?
Mode [1-4] (default 4): 4
```

### 7. Run tests

```bash
pytest
```

---

## Sample Interactions

The examples below show Mode 4 (Full Agentic) behavior. Each response includes the retrieved sources, the generated code, and the plain-language explanation.

---

### Example 1: Algorithm Implementation

**User input:**
```
How do I implement binary search in Python?
```

**Research Agent output:**
```
Retrieved 2 passages:

[binary_search.md] Binary search requires a sorted array. It eliminates half
the search space at each step by comparing the target to the midpoint element.
Time complexity: O(log n). Space complexity: O(1) for iterative, O(log n) for
recursive due to call stack.

[complexity_guide.md] Divide-and-conquer algorithms split a problem in half
each iteration. For n=1,000,000 elements, binary search needs at most 20 comparisons.
```

**Code Agent output:**
```python
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2   # avoids integer overflow vs (left+right)//2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # target not found
```

**Explainer Agent output:**
```
What this code does, step by step:

1. We define two pointers (left, right) that mark the current search window.
   We start with the full array.

2. Each loop iteration, we compute the midpoint. The formula `left + (right - left) // 2`
   is intentional — it prevents integer overflow that can happen with `(left + right) // 2`
   in languages with fixed integer sizes (like C/Java). Python doesn't overflow, but
   this is a good habit.

3. We compare arr[mid] to the target:
   - Equal: we found it, return its index
   - Too small: the target must be in the RIGHT half — move left pointer up
   - Too large: the target must be in the LEFT half — move right pointer down

4. If the loop ends without finding the target, we return -1 (Python convention
   for "not found").

Why not use recursion? The iterative version uses O(1) space. A recursive version
would use O(log n) stack frames — fine for most cases, but iterative is preferred
in production code for large inputs.

Source used: binary_search.md, complexity_guide.md
```

---

### Example 2: Design Pattern Guidance

**User input:**
```
What is the Observer pattern and when should I use it?
```

**Research Agent output:**
```
Retrieved 2 passages:

[observer_pattern.md] The Observer pattern defines a one-to-many dependency
between objects. When one object (the Subject) changes state, all its dependents
(Observers) are notified automatically. Common in event systems, MVC frameworks,
and reactive programming.

[design_patterns_overview.md] Behavioral patterns describe how objects communicate.
The Observer decouples the subject from its observers — the subject doesn't need
to know what the observers do with the notification, only that they exist.
```

**Code Agent output:**
```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: dict) -> None:
        pass

class Subject:
    def __init__(self):
        self._observers: list[Observer] = []
        self._state: dict = {}

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str) -> None:
        for observer in self._observers:
            observer.update(event, self._state)

    def set_state(self, key: str, value) -> None:
        self._state[key] = value
        self.notify(f"state_changed:{key}")


# Example usage
class Logger(Observer):
    def update(self, event: str, data: dict) -> None:
        print(f"[LOG] Event: {event} | State: {data}")

class Dashboard(Observer):
    def update(self, event: str, data: dict) -> None:
        print(f"[DASHBOARD] Refreshing with: {data}")
```

**Explainer Agent output:**
```
When to use Observer:

Use Observer when multiple parts of your system need to react to the same event,
but you don't want those parts to be tightly coupled to each other.

Real-world examples where Observer fits:
- A stock ticker that notifies a chart widget, a portfolio tracker, and an alert
  system every time the price changes — each reacts differently, but the ticker
  doesn't need to know about any of them.
- A game where an enemy's health bar, the score counter, and the audio system all
  need to react when the enemy takes damage.
- This project: when a new document is indexed, the embedding pipeline, the
  summary cache, and the UI search index all need to update.

When NOT to use Observer:
- When there is only one consumer — regular function calls are clearer.
- When order of notification matters and is complex — Observer doesn't guarantee order.
- When you need the result of the notification — use a different pattern (e.g. Command).
```

---

### Example 3: Comparing Algorithms

**User input:**
```
What's the difference between quicksort and mergesort? Which should I use?
```

**Research Agent output (abbreviated):**
```
Retrieved 3 passages from sorting_algorithms.md covering:
- Quicksort: O(n log n) average, O(n²) worst case, in-place, unstable
- Mergesort: O(n log n) all cases, O(n) extra space, stable
- When stability matters: sorting objects with multiple keys (e.g., sort by name,
  then by age while keeping name-sort intact)
```

**Code Agent + Explainer output (summary):**
```
Decision guide generated:

Use MERGESORT when:
- You need a stable sort (equal elements preserve their original order)
- Input size is large and worst-case O(n²) is unacceptable
- You're sorting linked lists (mergesort is natural for linked structures)
- Python's built-in sorted() uses Timsort, a mergesort hybrid — prefer that

Use QUICKSORT when:
- Memory is a constraint (in-place, O(log n) stack space average)
- Average case performance is what you optimize for
- You control the pivot strategy (random pivot avoids O(n²) on sorted input)

For most Python work: use sorted() or list.sort() — they're implemented in C,
use Timsort, and beat any pure-Python implementation.
```

---

## Design Decisions

### Why Claude API instead of Gemini?

DocuBot used the Gemini API. This project switches to the Anthropic Claude API for two reasons:
1. **Ecosystem alignment:** The course developer environment uses Claude Code (CLI and VSCode), so Claude is the natural choice for understanding how the tools work together.
2. **Tool use and agentic features:** The Anthropic API has a mature tool-use API (`tools` parameter) that makes building explicit agent loops straightforward without third-party frameworks.

Trade-off: Students familiar with Gemini from Module 4 need to learn a new SDK. The APIs are structurally similar enough that the transition is low-friction.

### Why ChromaDB instead of a manual inverted index?

DocuBot's inverted index worked well for keyword overlap, but it fails on semantic queries. A user asking "how do I find something in a sorted list?" should retrieve binary search documentation even if the words don't overlap exactly. ChromaDB stores sentence embeddings and finds semantically similar passages using vector cosine similarity.

Trade-off: ChromaDB adds a dependency and requires an initial indexing step. The old keyword search was zero-setup. The semantic quality improvement is worth this cost for a knowledge-heavy use case.

### Why sentence-transformers for embeddings?

Two alternatives were `all-MiniLM-L6-v2` from sentence-transformers (local, free) versus Claude's or OpenAI's embedding APIs (higher quality, requires API calls per indexed document).

Local embeddings were chosen because:
- Indexing runs once, locally, without per-call API costs
- The model is fast (runs in seconds on CPU for a small corpus)
- Query-time embedding is cheap (one embedding per query, not per document)

### Why explicit agents instead of a single prompt?

A single Claude prompt that does research + code + explanation produces results, but they are harder to evaluate and control individually. Separating concerns into three agents means:
- Each agent can be tested and swapped independently
- Users can run only the agents they need (e.g., explanation-only for existing code)
- Agent outputs are auditable at each step

Trade-off: More API calls per interaction (latency increases). Mitigated by async invocation where agents can run in parallel.

### Why keep all four modes (including naive LLM)?

Mode 1 (naive LLM) is retained as a baseline, not because it's recommended, but because comparing Mode 1 vs Mode 4 makes the value of retrieval and agent orchestration visible. This mirrors the pedagogical goal of the course: understand the architecture, not just use the tool.

---

## Testing Summary

### What works

- Semantic retrieval correctly handles paraphrase queries that would fail keyword search
  (e.g., "finding items in an ordered sequence" → retrieves binary search docs)
- The agent separation makes individual component testing straightforward
- ChromaDB's persistence means the index survives restarts without re-embedding

### What did not work as expected

- Very short queries (1-2 words, e.g., "sorting") retrieve too many low-relevance
  passages — minimum query length or query expansion helps
- The Explainer Agent sometimes re-explains the Code Agent's inline comments verbatim
  rather than adding new context — prompt refinement is ongoing
- Naive LLM mode (Mode 1) produces longer but less grounded answers, confirming
  that retrieval improves precision at the cost of some recall breadth

### What was learned

Retrieval quality has a bigger impact on final output quality than prompt quality.
A mediocre prompt with good retrieved context outperforms a great prompt with poor
context. This reinforces the DocuBot lesson from Module 4 but at larger scale.

Agent orchestration adds latency but adds disproportionate explainability. The
Explainer Agent alone — even when the code is correct — doubles a junior developer's
ability to understand and modify the output.

---

## Reflection

### What this project taught about AI and problem-solving

Building DocuBot in Module 4 made the RAG pattern legible. Extending it to an agentic
system revealed the next layer: retrieval quality is not the only variable. The quality
of context formatting (how snippets are presented in the prompt), the specificity of
agent instructions, and the separation of concerns between agents all matter as much
as what gets retrieved.

The transparency goal — helping programmers understand what AI builds — forced an
architectural decision that would not exist in a pure productivity tool: the Explainer
Agent exists not because it makes the code more correct, but because understanding
matters as much as correctness for learning. This is a values choice encoded into
architecture, the same lesson learned in the Music Recommender's bias analysis (Module 3).

AI tools change what problems programmers spend time on, not whether they have problems.
AlgoAssist doesn't eliminate the need to understand algorithms — it accelerates the path
to understanding them by grounding every AI output in citable, readable source material.

---

## Module Progression Context

This project draws directly on skills built across all four modules:

| Module | Skill Applied Here |
|--------|--------------------|
| Module 1 (Game Glitch Investigator) | Debugging logic and testing individual components in isolation |
| Module 1 (Playlist Chaos) | Edge case thinking: what happens when inputs don't match expectations |
| Module 2 (PawPal Scheduler) | Upfront system design before implementation; dataclass modeling |
| Module 3 (Music Recommender) | Scoring, evaluation methodology, bias awareness in AI outputs |
| Module 3 (Mood Machine) | Text preprocessing, tokenization, rule-based vs ML trade-offs |
| Module 4 (DocuBot) | RAG architecture, inverted indexing, LLM prompt construction — the direct foundation |

---

## Project Structure

```
ai110-applied-ai-systems-project/
├── app.py                  # Streamlit UI entry point
├── main.py                 # CLI entry point
├── build_index.py          # One-time script to embed and index knowledge base docs
├── models.py               # Shared dataclasses — input/output contracts for all agents
├── .env.example            # Template for environment variables
├── requirements.txt
├── README.md               # This file
│
├── assets/
│   ├── design_doc.md       # System design document with architecture and data shapes
│   └── diagram.md          # Mermaid architecture diagram
│
├── agents/
│   ├── orchestrator.py     # Routes queries, sequences agent calls
│   ├── research_agent.py   # Handles RAG retrieval and passage selection
│   ├── code_agent.py       # Generates grounded code using Claude API
│   └── explainer_agent.py  # Produces plain-language code breakdowns
│
├── rag/
│   ├── embedder.py         # sentence-transformers embedding wrapper
│   ├── vector_store.py     # ChromaDB interface (index, query, persist)
│   └── retriever.py        # Top-k retrieval with source attribution
│
├── knowledge_base/
│   └── docs/               # Markdown files: algorithms, data structures, patterns
│       ├── binary_search.md
│       ├── sorting_algorithms.md
│       ├── graph_traversal.md
│       ├── dynamic_programming.md
│       ├── design_patterns/
│       └── complexity_guide.md
│
├── evaluation/
│   ├── eval_retrieval.py   # Hit-rate evaluation (extends DocuBot's evaluation.py)
│   └── eval_queries.py     # Sample query set with expected source documents
│
└── tests/
    ├── test_retrieval.py
    ├── test_agents.py
    └── test_integration.py
```

---

## Requirements

- Python 3.11+
- `ANTHROPIC_API_KEY` for Modes 1, 3, and 4 (Claude API)
- No external server, no database setup beyond local ChromaDB persistence
- internet connection only required for initial model download (sentence-transformers)
  and Claude API calls
