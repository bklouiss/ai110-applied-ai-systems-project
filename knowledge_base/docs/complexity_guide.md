# Complexity Guide

## Overview

Algorithmic complexity describes how the resource requirements (time or memory) of an algorithm scale as input size n grows. Big O notation expresses the asymptotic upper bound on growth rate, abstracting away constant factors and lower-order terms.

---

## Big O Classes

| Notation   | Name          | Example Algorithm                          |
|------------|---------------|--------------------------------------------|
| O(1)       | Constant      | Hash map lookup, array index access        |
| O(log n)   | Logarithmic   | Binary search                              |
| O(n)       | Linear        | Linear search, single-pass array traversal |
| O(n log n) | Linearithmic  | Mergesort, Timsort, Heapsort               |
| O(n²)      | Quadratic     | Bubble sort, naive nested loops            |
| O(2ⁿ)      | Exponential   | Naive recursive Fibonacci, subset generation|
| O(n!)      | Factorial     | Naive traveling salesman, permutations     |

---

## Simplification Rules

- **Drop constants:** O(3n) → O(n)
- **Drop lower-order terms:** O(n² + n) → O(n²)
- **Worst case by default:** Unless otherwise stated, Big O expresses the worst-case scenario.
- **Amortized complexity:** The average cost per operation over a sequence. A dynamic array append is O(1) amortized despite occasional O(n) resize operations.

---

## Space Complexity

Measures auxiliary memory consumed beyond the input itself.

- **In-place algorithms:** O(1) auxiliary space (e.g., iterative binary search, heapsort, quicksort average).
- **Recursive algorithms:** O(depth) stack space even with no explicit data structures (e.g., DFS on a graph with depth d uses O(d) stack space).
- **Auxiliary arrays:** Mergesort requires O(n) extra space for the temporary merge buffer.

---

## Practical Benchmarks (n = 1,000,000)

| Complexity | Approximate Operations | Feasibility at n = 10⁶  |
|------------|------------------------|--------------------------|
| O(log n)   | ~20                    | Instant                  |
| O(n)       | 1,000,000              | Fast (~milliseconds)     |
| O(n log n) | ~20,000,000            | Fast (~tens of ms)       |
| O(n²)      | 10¹²                   | Too slow (days)          |
| O(2ⁿ)      | 10^301,030             | Infeasible               |

---

## Common Python Pitfalls

- **`in` on a list:** O(n) — scans every element. Use a `set` for O(1) membership testing.
- **String concatenation in a loop:** `s += chunk` is O(n²) total because each `+` copies the entire string. Use `''.join(parts)` instead.
- **Recursive depth limit:** Python's default is 1,000. Deep recursive algorithms (DFS, recursive DP) may hit `RecursionError`. Use iterative implementations or `sys.setrecursionlimit` with care.
- **Sorting already-sorted data:** Most O(n log n) sorts degrade on sorted input with naive pivot selection. Python's Timsort handles this gracefully (O(n) best case).
