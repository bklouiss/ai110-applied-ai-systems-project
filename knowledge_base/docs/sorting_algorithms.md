# Sorting Algorithms

## Overview

Sorting algorithms arrange elements of a collection into a defined order (typically ascending). The right choice depends on input size, memory constraints, stability requirements, and whether the data arrives partially sorted.

---

## Algorithm Comparison

| Algorithm      | Best       | Average    | Worst      | Space    | Stable |
|----------------|------------|------------|------------|----------|--------|
| Quicksort      | O(n log n) | O(n log n) | O(n²)      | O(log n) | No     |
| Mergesort      | O(n log n) | O(n log n) | O(n log n) | O(n)     | Yes    |
| Heapsort       | O(n log n) | O(n log n) | O(n log n) | O(1)     | No     |
| Timsort        | O(n)       | O(n log n) | O(n log n) | O(n)     | Yes    |
| Insertion Sort | O(n)       | O(n²)      | O(n²)      | O(1)     | Yes    |

---

## Quicksort

Divide-and-conquer: selects a pivot, partitions the array so all elements smaller than the pivot precede it and all larger elements follow it, then recursively sorts each partition.

- **In-place:** Uses O(log n) average stack space; no auxiliary array required.
- **Unstable:** Equal elements may be reordered relative to their original positions.
- **Worst case O(n²):** Triggered by consistently poor pivot choice (e.g., always picking the smallest or largest element on a sorted input). Random pivot selection or the median-of-three strategy eliminates this in practice.

---

## Mergesort

Divide-and-conquer: recursively splits the array into halves until each subarray has one element, then merges the sorted halves back in order.

- **Stable:** Equal elements preserve their original relative order.
- **Guaranteed O(n log n):** No worst-case degradation regardless of input shape.
- **O(n) auxiliary space:** Requires a temporary array during merging.
- **Best for:** Linked lists (merging is natural), external sorting (disk-based), and any context where stability is required.

---

## Timsort

Python's built-in sort algorithm (used by `sorted()` and `list.sort()`). A hybrid of Mergesort and Insertion Sort that detects and exploits naturally ordered runs in real-world data.

- **Best case O(n)** on already-sorted or reverse-sorted input.
- Runs in C — always faster than any pure-Python sorting implementation.
- **Always prefer Timsort in Python** for production code.

---

## Decision Guide

| Situation | Recommended |
|-----------|-------------|
| General Python sorting | `sorted()` or `list.sort()` — Timsort, implemented in C |
| Stable sort required | Mergesort or Timsort |
| Memory-constrained, average case matters | Quicksort with random pivot |
| Guaranteed worst-case O(n log n), in-place | Heapsort |
| Small (n < 20) or nearly-sorted input | Insertion Sort |

---

## Stability Explained

A sort is **stable** if equal elements appear in the same relative order in the output as in the input. Stability matters when sorting objects by multiple keys: if you sort a list of people by age and the sort is stable, people with the same age preserve their original name order from a prior sort.
