# Graph Traversal

## Overview

Graph traversal algorithms systematically visit every vertex in a graph. The two fundamental strategies are Breadth-First Search (BFS) and Depth-First Search (DFS), each with distinct traversal order, memory characteristics, and appropriate use cases.

---

## Graph Representations

- **Adjacency list:** `dict[node, list[neighbors]]` — O(V + E) space. Efficient for sparse graphs and iterating over neighbors.
- **Adjacency matrix:** `list[list[int]]` — O(V²) space. Efficient for dense graphs and O(1) edge existence checks.

---

## Breadth-First Search (BFS)

Explores all neighbors at the current depth level before advancing to the next. Uses a **queue** (FIFO).

**Complexity:** O(V + E) time, O(V) space.

### Use Cases
- **Shortest path in an unweighted graph** — BFS guarantees the minimum number of edges.
- Level-order traversal of a tree.
- Finding all nodes within k hops of a source.
- Testing whether a graph is bipartite.

---

## Depth-First Search (DFS)

Explores as far as possible along each branch before backtracking. Uses a **stack** (explicit or the call stack via recursion).

**Complexity:** O(V + E) time, O(V) space.

### Use Cases
- **Cycle detection** in directed and undirected graphs.
- **Topological sort** of a directed acyclic graph (DAG).
- Finding all connected components.
- Generating spanning trees.
- Maze solving and path existence queries.

---

## BFS vs DFS Comparison

| Property | BFS | DFS |
|----------|-----|-----|
| Data structure | Queue (deque) | Stack / recursion |
| Finds shortest path (unweighted) | Yes | No |
| Memory on wide graphs | High | Low |
| Memory on deep graphs | Low | High (stack overflow risk) |
| Visits all reachable nodes | Yes | Yes |
| Natural for level-by-level processing | Yes | No |

---

## Weighted Shortest Path

BFS finds the shortest path in terms of **edge count** only. For weighted graphs:

- **Dijkstra's algorithm** — shortest path with non-negative edge weights. O((V + E) log V) with a min-heap.
- **Bellman-Ford** — handles negative edge weights. O(V · E).
- **A\*** — heuristic-guided shortest path for spatial graphs.

---

## Iterative DFS vs Recursive DFS

Recursive DFS is cleaner to write but risks stack overflow on deep graphs (Python's default recursion limit is 1,000). For large graphs, prefer an explicit stack with an iterative DFS implementation.
