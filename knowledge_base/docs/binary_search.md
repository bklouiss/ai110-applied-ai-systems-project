# Binary Search

## Overview

Binary search is a divide-and-conquer algorithm for locating a target value in a sorted array. At each step it compares the target to the midpoint element and eliminates half the remaining search space, achieving O(log n) time complexity.

**Prerequisite:** The input array must be sorted in ascending order.

---

## Complexity

| Case    | Time      | Space (iterative) | Space (recursive) |
|---------|-----------|-------------------|-------------------|
| Best    | O(1)      | O(1)              | O(log n)          |
| Average | O(log n)  | O(1)              | O(log n)          |
| Worst   | O(log n)  | O(1)              | O(log n)          |

---

## Key Concepts

- **Search window:** Defined by `left` and `right` pointer indices that narrow on each iteration.
- **Midpoint formula:** Use `left + (right - left) // 2` rather than `(left + right) // 2` to avoid integer overflow in fixed-width integer languages (C, Java). Python integers don't overflow, but the habit is worth keeping.
- **Termination:** The loop exits when `left > right`, meaning the target is absent.
- **Return value:** Return the index of the found element, or -1 (not found). Returning `left` instead of -1 gives the sorted insertion point.

---

## Variants

- **Iterative:** O(1) auxiliary space. Preferred for production.
- **Recursive:** O(log n) stack space due to call frames. Cleaner to read but not preferred for large inputs.
- **Finding the left boundary:** Useful for finding the first occurrence in an array with duplicates.
- **Binary search on answer:** Apply binary search to a monotonic function's domain rather than an array (e.g., minimum feasible value problems).

---

## When to Use

- Searching in any sorted sequence (array, tuple, sorted dictionary keys).
- Finding the boundary of a monotonic condition ("smallest x where f(x) is true").
- Autocomplete and range queries in sorted data structures.

---

## When Not to Use

- Unsorted data — sort first at O(n log n) cost, or use a hash map for O(1) lookup.
- Very small arrays (n < ~16) — linear search has lower constant overhead.
- Linked lists — no O(1) random access, so midpoint lookup degrades to O(n).
