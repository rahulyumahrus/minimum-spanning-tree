# minimum-spanning-tree

Computes a minimum-weight spanning tree of an edge-weighted undirected graph using Kruskal's algorithm and a disjoint-set structure.

## Usage

```python
from minimum_spanning_tree import Edge, Graph, kruskal_mst

edges = [
    Edge("a", "b", 1.0),
    Edge("b", "c", 2.0),
    Edge("a", "c", 3.0),
]
graph = Graph(edges)
mst = kruskal_mst(graph)
print(mst)
# [Edge(u='a', v='b', weight=1.0), Edge(u='b', v='c', weight=2.0)]
```

## Why this exists

Finding a minimum spanning tree is a classic problem with several well-known algorithms. Kruskal's algorithm was chosen because it operates directly on a list of edges, which makes the input model simple and avoids requiring adjacency lists or matrix representations. The main trade-off is sorting cost: Kruskal's algorithm runs in O(E log E) time, whereas Prim's algorithm with a binary heap can achieve O(E log V). For most practical graphs the difference is negligible, and the edge-list API is often easier to integrate.

Edge weights are required to be non-negative. This restriction is not fundamental to Kruskal's algorithm, but it prevents ambiguity about what "minimum" means when negative weights are allowed and keeps the library focused on the common case of distances or costs.

## Edge cases

- A disconnected graph produces a minimum spanning forest rather than a single spanning tree.
- Duplicate edges (same endpoints and weight) are automatically removed when a `Graph` is constructed.
- Edges are immutable (`frozen=True`) so sorting remains stable and safe.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

