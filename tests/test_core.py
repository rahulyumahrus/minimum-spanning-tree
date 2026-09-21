"""Tests for minimum_spanning_tree.core."""

import unittest

from minimum_spanning_tree.core import Edge, Graph, kruskal_mst


class TestEdge(unittest.TestCase):
    def test_edge_is_frozen(self):
        e = Edge("a", "b", 1.0)
        with self.assertRaises(AttributeError):
            e.weight = 2.0

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            Edge("a", "b", -0.1)


class TestGraph(unittest.TestCase):
    def test_empty_graph(self):
        g = Graph()
        self.assertEqual(g.edges, ())
        self.assertEqual(g.vertices, frozenset())

    def test_vertices_collected_from_edges(self):
        g = Graph([Edge(1, 2, 1.0), Edge(2, 3, 2.0)])
        self.assertEqual(g.vertices, frozenset({1, 2, 3}))

    def test_duplicate_edges_removed(self):
        e = Edge("x", "y", 5.0)
        g = Graph([e, e, Edge("x", "y", 5.0)])
        self.assertEqual(len(g.edges), 1)
        self.assertEqual(g.edges[0], e)


class TestKruskalMST(unittest.TestCase):
    def test_empty_graph_returns_empty_list(self):
        self.assertEqual(kruskal_mst(Graph()), [])

    def test_single_edge(self):
        g = Graph([Edge("a", "b", 2.0)])
        self.assertEqual(kruskal_mst(g), [Edge("a", "b", 2.0)])

    def test_simple_triangle(self):
        g = Graph(
            [
                Edge("a", "b", 1.0),
                Edge("b", "c", 2.0),
                Edge("a", "c", 3.0),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 2)
        self.assertIn(Edge("a", "b", 1.0), mst)
        self.assertIn(Edge("b", "c", 2.0), mst)
        self.assertNotIn(Edge("a", "c", 3.0), mst)

    def test_tie_weights_are_handled_deterministically(self):
        # All weights equal. The sorted order is deterministic because edges
        # compare by dataclass field order: u, then v, then weight.
        edges = [
            Edge(1, 2, 1.0),
            Edge(2, 3, 1.0),
            Edge(3, 4, 1.0),
            Edge(4, 1, 1.0),
            Edge(1, 3, 1.0),
        ]
        g = Graph(edges)
        mst = kruskal_mst(g)
        # For 4 vertices, an MST has exactly 3 edges.
        self.assertEqual(len(mst), 3)
        # The result must be connected: every vertex appears at least once.
        vertices_in_mst = set()
        for e in mst:
            vertices_in_mst.add(e.u)
            vertices_in_mst.add(e.v)
        self.assertEqual(vertices_in_mst, {1, 2, 3, 4})

    def test_disconnected_graph_returns_spanning_forest(self):
        g = Graph(
            [
                Edge("a", "b", 1.0),
                Edge("c", "d", 2.0),
                Edge("e", "f", 3.0),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 3)
        # Every original edge is chosen because no cycles are possible.
        for e in g.edges:
            self.assertIn(e, mst)

    def test_cycle_with_heavy_edges_excluded(self):
        g = Graph(
            [
                Edge("a", "b", 1.0),
                Edge("b", "c", 2.0),
                Edge("c", "d", 3.0),
                Edge("d", "a", 100.0),
                Edge("a", "c", 50.0),
                Edge("b", "d", 60.0),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 3)
        self.assertIn(Edge("a", "b", 1.0), mst)
        self.assertIn(Edge("b", "c", 2.0), mst)
        self.assertIn(Edge("c", "d", 3.0), mst)

    def test_mst_weight_is_minimal(self):
        g = Graph(
            [
                Edge("a", "b", 1.0),
                Edge("b", "c", 2.0),
                Edge("a", "c", 2.5),
                Edge("c", "d", 1.5),
                Edge("b", "d", 3.0),
            ]
        )
        mst = kruskal_mst(g)
        total = sum(e.weight for e in mst)
        self.assertEqual(total, 4.5)

    def test_float_weights_are_supported(self):
        g = Graph(
            [
                Edge(1, 2, 0.5),
                Edge(2, 3, 0.25),
                Edge(1, 3, 0.75),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 2)
        self.assertIn(Edge(2, 3, 0.25), mst)
        self.assertIn(Edge(1, 2, 0.5), mst)

    def test_large_weight_differences(self):
        g = Graph(
            [
                Edge("a", "b", 1e9),
                Edge("b", "c", 1e-9),
                Edge("a", "c", 5e8),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 2)
        self.assertIn(Edge("b", "c", 1e-9), mst)
        self.assertIn(Edge("a", "c", 5e8), mst)

    def test_custom_hashable_vertices(self):
        g = Graph(
            [
                Edge((1, 2), (3, 4), 1.0),
                Edge((3, 4), (5, 6), 2.0),
            ]
        )
        mst = kruskal_mst(g)
        self.assertEqual(len(mst), 2)


if __name__ == "__main__":
    unittest.main()
