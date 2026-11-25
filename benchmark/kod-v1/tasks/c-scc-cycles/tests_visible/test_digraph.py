import unittest

from digraph import DiGraph, components, condensation_edges, cyclic_components, is_acyclic


def build(edges, extra=()):
    graph = DiGraph()
    for node in extra:
        graph.add_node(node)
    for source, target in edges:
        graph.add_edge(source, target)
    return graph


class VisibleTests(unittest.TestCase):
    def test_two_cycles_and_a_bridge(self):
        graph = build([("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("d", "c")])
        self.assertEqual(components(graph), [["a", "b"], ["c", "d"]])
        self.assertEqual(cyclic_components(graph), [["a", "b"], ["c", "d"]])
        self.assertFalse(is_acyclic(graph))

    def test_isolated_node_is_its_own_component(self):
        graph = build([("x", "y")], extra=["m"])
        self.assertEqual(graph.nodes(), ["m", "x", "y"])
        self.assertEqual(components(graph), [["m"], ["x"], ["y"]])
        self.assertTrue(is_acyclic(graph))

    def test_self_loop_counts_as_cycle(self):
        graph = build([("p", "p"), ("p", "q")])
        self.assertEqual(cyclic_components(graph), [["p"]])
        self.assertFalse(is_acyclic(graph))
        self.assertEqual(graph.edge_count(), 2)

    def test_condensation_of_chain(self):
        graph = build([("a", "b"), ("b", "c")])
        self.assertEqual(condensation_edges(graph), [(0, 1), (1, 2)])


if __name__ == "__main__":
    unittest.main()
