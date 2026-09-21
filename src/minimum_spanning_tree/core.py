"""Core implementation of Kruskal's minimum spanning tree algorithm.

The graph is represented as an explicit list of edges, where each edge is an
undirected connection between two vertices and carries a numeric weight. The
implementation uses Kruskal's algorithm with a union-find (disjoint-set) data
structure and path compression plus union by rank for efficiency.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T", bound=Any)


@dataclass(frozen=True)
class Edge(Generic[T]):
    """An undirected weighted edge between two vertices.

    The edge is immutable because Kruskal's algorithm relies on sorting edges;
    mutating an edge after it has been placed in the sorted list would break
    the algorithm's correctness.
    """

    u: T
    v: T
    weight: float

    def __post_init__(self) -> None:
        if self.weight < 0:
            # Negative weights are valid in general graph theory, but Kruskal's
            # algorithm still works with them. We reject them only to keep the
            # meaning of "minimum" unambiguous for callers who expect
            # non-negative distances. This is documented in the README.
            raise ValueError("edge weights must be non-negative")


class DisjointSet(Generic[T]):
    """Union-find data structure with path compression and union by rank."""

    def __init__(self) -> None:
        self._parent: dict[T, T] = {}
        self._rank: dict[T, int] = {}

    def make_set(self, item: T) -> None:
        if item not in self._parent:
            self._parent[item] = item
            self._rank[item] = 0

    def find(self, item: T) -> T:
        if item not in self._parent:
            raise KeyError(item)
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        # Path compression: point every node on the path directly to the root.
        while self._parent[item] != item:
            next_item = self._parent[item]
            self._parent[item] = root
            item = next_item
        return root

    def union(self, a: T, b: T) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        rank_a = self._rank[root_a]
        rank_b = self._rank[root_b]
        if rank_a < rank_b:
            self._parent[root_a] = root_b
        elif rank_a > rank_b:
            self._parent[root_b] = root_a
        else:
            self._parent[root_b] = root_a
            self._rank[root_a] += 1


class Graph(Generic[T]):
    """An undirected weighted graph backed by a list of edges.

    Vertices are discovered from the edge list; there is no separate vertex
    registry. This keeps the API minimal and makes it easy to construct a
    graph from an arbitrary edge collection.
    """

    def __init__(self, edges: Iterable[Edge[T]] = ()) -> None:
        self._edges = list(edges)
        # De-duplicate identical edges (same endpoints and weight) to avoid
        # pointless work in Kruskal's algorithm. Order is preserved.
        seen: set[Edge[T]] = set()
        unique: list[Edge[T]] = []
        for edge in self._edges:
            if edge not in seen:
                seen.add(edge)
                unique.append(edge)
        self._edges = unique

    @property
    def edges(self) -> Sequence[Edge[T]]:
        """Return the graph's edges as an immutable sequence."""
        return tuple(self._edges)

    @property
    def vertices(self) -> frozenset[T]:
        """Return the set of vertices that appear in at least one edge."""
        vs: set[T] = set()
        for edge in self._edges:
            vs.add(edge.u)
            vs.add(edge.v)
        return frozenset(vs)


def kruskal_mst(graph: Graph[T]) -> list[Edge[T]]:
    """Compute a minimum spanning tree of *graph*.

    Returns a list of edges that form an MST. If the graph is disconnected,
    the result is a minimum spanning forest (one spanning tree per connected
    component). The empty graph returns an empty list.

    Kruskal's algorithm is used because it is simple, deterministic, and works
    naturally on an explicit edge list without requiring adjacency information.
    Its time complexity is O(E log E) dominated by sorting.
    """
    if not graph.edges:
        return []

    ds: DisjointSet[T] = DisjointSet()
    for v in graph.vertices:
        ds.make_set(v)

    mst_edges: list[Edge[T]] = []
    for edge in sorted(graph.edges, key=lambda e: e.weight):
        if ds.find(edge.u) != ds.find(edge.v):
            ds.union(edge.u, edge.v)
            mst_edges.append(edge)
    return mst_edges
