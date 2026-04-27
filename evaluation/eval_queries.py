"""
evaluation/eval_queries.py
--------------------------
Sample query set used for retrieval evaluation. Each entry pairs a natural-language
query with the expected source document filename(s) that should appear in the top-k
retrieved passages. Covers semantic paraphrase cases (where keyword overlap would
fail), exact-term cases, and multi-document queries to stress-test retrieval quality
across the full knowledge base.

Used by eval_retrieval.py to compute hit rate.
"""

EVAL_QUERIES: list[dict] = [
    # Each entry: {"query": str, "expected_sources": list[str]}

    # Binary search — exact and paraphrase
    {
        "query": "How do I implement binary search in Python?",
        "expected_sources": ["binary_search.md"],
    },
    {
        "query": "finding items in an ordered sequence",
        "expected_sources": ["binary_search.md"],
    },

    # Sorting — exact and paraphrase
    {
        "query": "What is the time complexity of quicksort?",
        "expected_sources": ["sorting_algorithms.md"],
    },
    {
        "query": "difference between quicksort and mergesort",
        "expected_sources": ["sorting_algorithms.md"],
    },

    # Graph traversal — exact and paraphrase
    {
        "query": "how to traverse a graph",
        "expected_sources": ["graph_traversal.md"],
    },
    {
        "query": "BFS vs DFS when to use each",
        "expected_sources": ["graph_traversal.md"],
    },

    # Dynamic programming — paraphrase
    {
        "query": "memoization and overlapping subproblems",
        "expected_sources": ["dynamic_programming.md"],
    },
    {
        "query": "breaking a problem into smaller subproblems",
        "expected_sources": ["dynamic_programming.md"],
    },

    # Design patterns
    {
        "query": "Observer pattern event system",
        "expected_sources": ["design_patterns/observer_pattern.md"],
    },

    # Complexity — exact and multi-doc
    {
        "query": "Big O notation explained",
        "expected_sources": ["complexity_guide.md"],
    },
    {
        "query": "O(n log n) sorting algorithm with guaranteed worst case",
        "expected_sources": ["sorting_algorithms.md", "complexity_guide.md"],
    },
]
