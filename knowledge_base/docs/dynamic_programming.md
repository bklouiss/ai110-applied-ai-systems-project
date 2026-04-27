# Dynamic Programming

## Overview

Dynamic programming (DP) solves complex problems by breaking them into overlapping subproblems and caching intermediate results to avoid redundant computation. It applies when a problem exhibits two properties: **optimal substructure** and **overlapping subproblems**.

---

## Core Properties

### Optimal Substructure
The globally optimal solution can be built from locally optimal solutions to subproblems. (Not all greedy problems have this; DP requires that the subproblem solutions actually combine correctly.)

### Overlapping Subproblems
The same subproblems are encountered repeatedly in a naive recursive approach. DP stores results the first time each subproblem is solved to avoid recomputing them.

---

## Approaches

### Top-Down (Memoization)
Start with the original problem, recurse into subproblems, and cache each result in a dictionary or array on the way back up.

- Follows the natural recursive structure of the problem.
- Only computes subproblems that are actually needed (lazy).
- Uses the call stack — risk of stack overflow for large inputs in Python.

### Bottom-Up (Tabulation)
Identify the smallest subproblems, solve them first, and build up to the original problem iteratively using a table.

- Iterative — no stack overflow risk.
- Often more space-efficient: rows no longer needed can be discarded.
- Requires understanding the subproblem dependency order upfront.

---

## Classic Problems

| Problem | Approach | Time | Space |
|---------|----------|------|-------|
| Fibonacci sequence | Memoization or tabulation | O(n) | O(n) or O(1) |
| 0/1 Knapsack | 2D tabulation | O(n · W) | O(n · W) |
| Longest Common Subsequence | 2D tabulation | O(m · n) | O(m · n) |
| Coin Change (min coins) | 1D tabulation | O(n · amount) | O(amount) |
| Edit Distance | 2D tabulation | O(m · n) | O(m · n) |
| Longest Increasing Subsequence | 1D DP or patience sorting | O(n²) or O(n log n) | O(n) |

---

## Identifying DP Problems

A problem is likely a DP candidate if it:
1. Asks for an **optimal value** (minimum, maximum, longest, shortest).
2. Asks whether a solution **exists** ("can you reach X?").
3. Asks to **count** the number of distinct ways to achieve a goal.
4. Has a natural recursive definition that re-solves the same subproblems.

---

## Space Optimization

Many 2D DP tables can be compressed to O(n) or even O(1) auxiliary space. If the recurrence for row `i` only depends on row `i-1`, store two rows and alternate. If it only depends on the immediately previous value, a single variable suffices (classic Fibonacci optimization).
