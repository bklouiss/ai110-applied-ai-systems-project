"""
evaluation/eval_retrieval.py
-----------------------------
Retrieval evaluation module. Measures hit rate: the fraction of queries in
EVAL_QUERIES for which at least one expected source document appears in the
top-k retrieved passages. Extends the evaluation approach from DocuBot (Module 4)
to the ChromaDB/sentence-transformers pipeline.

Run directly to print a summary report:
    python evaluation/eval_retrieval.py
"""

from models import Passage
from rag.retriever import Retriever
from evaluation.eval_queries import EVAL_QUERIES


def evaluate_hit_rate(k: int = 3) -> float:
    """
    Runs all queries from EVAL_QUERIES through the Retriever and calculates
    the fraction that return at least one expected source document in the
    top-k results. A query is a hit if any of its expected_sources appears
    in the sources of the retrieved passages.

    Args:
        k: Number of passages to retrieve per query. Defaults to 3.

    Returns:
        Hit rate as a float between 0.0 and 1.0.
    """
    return run_evaluation(k)["hit_rate"]


def run_evaluation(k: int = 3) -> dict:
    """
    Runs the full evaluation suite and returns a structured summary. Includes
    per-query results so callers can inspect which specific queries failed,
    which is useful for diagnosing retrieval weaknesses.

    Args:
        k: Number of passages to retrieve per query. Defaults to 3.

    Returns:
        Dict with keys:
            'hit_rate' (float): Overall fraction of hits.
            'total'    (int):   Total number of queries evaluated.
            'hits'     (int):   Number of queries with at least one source hit.
            'results'  (list):  Per-query dicts with 'query', 'expected_sources',
                                'retrieved_sources', and 'hit' (bool).
    """
    retriever = Retriever()
    results = []
    hits = 0

    for item in EVAL_QUERIES:
        passages = retriever.retrieve(item["query"], k=k)
        retrieved_sources = [p.source for p in passages]
        hit = any(expected in retrieved_sources for expected in item["expected_sources"])
        if hit:
            hits += 1
        results.append({
            "query": item["query"],
            "expected_sources": item["expected_sources"],
            "retrieved_sources": retrieved_sources,
            "hit": hit,
        })

    total = len(EVAL_QUERIES)
    return {
        "hit_rate": hits / total if total > 0 else 0.0,
        "total": total,
        "hits": hits,
        "results": results,
    }


if __name__ == "__main__":
    results = run_evaluation()
    print(f"Hit rate: {results['hit_rate']:.2%} ({results['hits']}/{results['total']})")
    for r in results["results"]:
        status = "HIT " if r["hit"] else "MISS"
        print(f"  [{status}] {r['query'][:60]}")
