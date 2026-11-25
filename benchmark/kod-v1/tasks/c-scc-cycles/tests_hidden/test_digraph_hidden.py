import unittest

from digraph import DiGraph, components, condensation_edges, cyclic_components, is_acyclic


NAMES = ["n%d" % i for i in range(9)]

GRAPH_FIXTURES = [
    [("n3", "n6"), ("n1", "n8"), ("n0", "n3"), ("n3", "n7"), ("n3", "n2"), ("n1", "n0"), ("n4", "n3"),
     ("n1", "n3"), ("n7", "n2")],
    [("n5", "n3"), ("n1", "n0"), ("n6", "n2"), ("n6", "n7"), ("n8", "n5"), ("n7", "n5"), ("n6", "n5"),
     ("n6", "n5"), ("n1", "n8"), ("n4", "n2"), ("n0", "n6"), ("n1", "n4")],
    [("n1", "n3"), ("n3", "n2"), ("n1", "n8"), ("n3", "n1"), ("n2", "n8"), ("n3", "n1"), ("n0", "n3"),
     ("n5", "n6"), ("n8", "n8"), ("n3", "n1"), ("n5", "n8"), ("n3", "n3")],
    [("n7", "n8"), ("n2", "n8"), ("n0", "n6"), ("n2", "n0"), ("n4", "n0"), ("n0", "n1"), ("n0", "n1"),
     ("n4", "n3"), ("n5", "n3"), ("n8", "n5"), ("n4", "n3"), ("n4", "n3"), ("n8", "n5"), ("n5", "n2")],
    [("n7", "n8"), ("n0", "n0"), ("n0", "n4"), ("n8", "n7"), ("n8", "n4"), ("n1", "n2"), ("n3", "n8"),
     ("n4", "n1"), ("n8", "n4"), ("n6", "n4"), ("n7", "n3"), ("n1", "n4"), ("n3", "n6"), ("n2", "n1"),
     ("n5", "n7")],
    [("n4", "n1"), ("n4", "n6"), ("n5", "n3"), ("n5", "n6"), ("n0", "n0"), ("n3", "n8"), ("n1", "n3"),
     ("n5", "n3"), ("n1", "n4"), ("n5", "n0"), ("n5", "n8"), ("n5", "n3"), ("n4", "n1"), ("n2", "n2"),
     ("n0", "n8"), ("n3", "n3")],
    [],
    [("n8", "n0"), ("n4", "n4"), ("n3", "n8"), ("n3", "n3"), ("n8", "n4"), ("n5", "n4"), ("n7", "n6"),
     ("n8", "n3"), ("n4", "n7"), ("n4", "n3"), ("n6", "n6"), ("n8", "n4"), ("n8", "n2")],
    [("n7", "n3"), ("n3", "n5"), ("n4", "n7"), ("n4", "n1"), ("n7", "n4"), ("n3", "n6"), ("n0", "n0"),
     ("n2", "n2"), ("n5", "n3")],
    [("n0", "n2"), ("n7", "n6"), ("n4", "n5"), ("n5", "n5"), ("n5", "n5"), ("n5", "n1"), ("n5", "n2"),
     ("n6", "n0"), ("n4", "n7"), ("n0", "n0"), ("n8", "n0"), ("n0", "n3"), ("n2", "n6"), ("n0", "n8"),
     ("n4", "n3"), ("n4", "n5")],
    [],
    [("n4", "n2")],
    [("n7", "n5")],
    [("n3", "n2"), ("n5", "n8"), ("n8", "n1"), ("n2", "n4"), ("n1", "n5"), ("n4", "n1"), ("n4", "n7"),
     ("n7", "n1"), ("n7", "n0"), ("n4", "n3"), ("n6", "n3"), ("n4", "n6"), ("n5", "n2"), ("n5", "n3"),
     ("n2", "n1"), ("n0", "n5")],
    [("n8", "n0"), ("n8", "n4"), ("n5", "n1"), ("n6", "n6"), ("n4", "n2"), ("n6", "n2"), ("n1", "n6"),
     ("n6", "n0"), ("n0", "n7")],
    [("n1", "n5"), ("n5", "n0"), ("n3", "n0"), ("n3", "n0"), ("n0", "n3"), ("n2", "n2"), ("n2", "n6"),
     ("n1", "n2")],
    [("n7", "n4"), ("n0", "n1"), ("n0", "n8"), ("n2", "n0"), ("n8", "n0"), ("n4", "n6"), ("n5", "n4"),
     ("n7", "n6"), ("n0", "n1"), ("n3", "n2"), ("n3", "n5"), ("n7", "n2"), ("n8", "n7"), ("n0", "n8")],
    [("n5", "n3")],
    [("n7", "n4")],
    [("n1", "n2"), ("n3", "n1"), ("n4", "n2"), ("n3", "n0"), ("n8", "n7"), ("n0", "n8"), ("n7", "n3"),
     ("n2", "n5")],
    [("n2", "n0"), ("n0", "n1"), ("n5", "n3"), ("n7", "n1"), ("n7", "n6")],
    [("n5", "n6"), ("n4", "n6"), ("n1", "n8"), ("n0", "n8"), ("n0", "n7"), ("n4", "n4"), ("n6", "n7"),
     ("n7", "n4"), ("n2", "n3"), ("n6", "n7"), ("n3", "n4"), ("n1", "n6")],
    [("n8", "n3"), ("n4", "n3"), ("n5", "n1"), ("n1", "n1"), ("n8", "n8"), ("n0", "n4"), ("n1", "n1")],
    [("n6", "n7"), ("n7", "n6"), ("n4", "n8"), ("n8", "n4")],
    [("n8", "n8"), ("n0", "n7")],
    [("n0", "n7")],
    [("n4", "n5"), ("n1", "n7"), ("n4", "n4"), ("n7", "n3"), ("n5", "n3"), ("n8", "n3"), ("n2", "n4"),
     ("n1", "n7")],
    [("n0", "n2"), ("n5", "n0"), ("n8", "n8"), ("n3", "n6"), ("n6", "n8"), ("n1", "n4"), ("n5", "n1"),
     ("n5", "n7"), ("n0", "n4"), ("n5", "n7")],
    [("n7", "n5"), ("n3", "n8"), ("n1", "n4"), ("n6", "n5"), ("n3", "n5"), ("n3", "n6"), ("n4", "n7"),
     ("n3", "n5"), ("n2", "n4")],
    [("n3", "n1"), ("n7", "n2"), ("n8", "n5"), ("n0", "n3"), ("n8", "n8"), ("n7", "n2"), ("n8", "n3"),
     ("n3", "n4")],
    [("n7", "n3"), ("n3", "n4"), ("n7", "n4")],
    [("n1", "n1"), ("n5", "n5"), ("n7", "n2"), ("n5", "n5"), ("n5", "n2"), ("n6", "n8"), ("n6", "n6"),
     ("n1", "n7")],
    [("n8", "n7"), ("n5", "n7"), ("n3", "n0"), ("n1", "n8"), ("n1", "n8"), ("n1", "n2"), ("n6", "n3"),
     ("n1", "n6"), ("n5", "n6"), ("n4", "n1")],
    [("n6", "n5"), ("n6", "n7"), ("n6", "n7"), ("n7", "n4"), ("n8", "n0"), ("n1", "n3"), ("n3", "n5"),
     ("n2", "n5"), ("n8", "n3")],
    [("n7", "n8"), ("n3", "n8"), ("n7", "n6"), ("n3", "n3"), ("n3", "n5"), ("n8", "n6"), ("n0", "n4"),
     ("n5", "n3"), ("n4", "n5"), ("n3", "n7"), ("n8", "n2"), ("n6", "n0"), ("n8", "n0"), ("n1", "n2"),
     ("n3", "n8")],
    [("n2", "n6"), ("n7", "n7"), ("n6", "n3"), ("n4", "n7"), ("n8", "n0")],
    [("n8", "n5"), ("n5", "n0"), ("n3", "n4"), ("n7", "n6"), ("n2", "n5"), ("n7", "n7"), ("n5", "n1"),
     ("n8", "n2"), ("n8", "n3"), ("n7", "n4"), ("n2", "n6")],
    [("n8", "n7"), ("n1", "n3"), ("n0", "n7"), ("n4", "n7"), ("n4", "n8"), ("n5", "n2"), ("n7", "n0"),
     ("n3", "n8"), ("n0", "n4"), ("n8", "n8"), ("n4", "n2"), ("n6", "n5"), ("n1", "n5"), ("n2", "n6"),
     ("n7", "n7")],
    [("n4", "n8"), ("n5", "n4"), ("n3", "n7"), ("n1", "n7"), ("n7", "n6"), ("n2", "n0"), ("n8", "n4"),
     ("n2", "n5")],
    [("n5", "n0"), ("n6", "n3"), ("n8", "n3"), ("n3", "n4"), ("n5", "n2"), ("n1", "n3"), ("n1", "n1")],
]


def build(edges, extra=()):
    graph = DiGraph()
    for node in extra:
        graph.add_node(node)
    for source, target in edges:
        graph.add_edge(source, target)
    return graph


def reachable(graph, start):
    seen = {start}
    todo = [start]
    while todo:
        node = todo.pop()
        for child in graph.successors(node):
            if child not in seen:
                seen.add(child)
                todo.append(child)
    return seen


class HiddenTests(unittest.TestCase):
    def test_cross_edge_into_finished_component(self):
        graph = build([("a", "b"), ("a", "c"), ("c", "b")])
        self.assertEqual(components(graph), [["a"], ["b"], ["c"]])
        self.assertTrue(is_acyclic(graph))
        self.assertEqual(condensation_edges(graph), [(0, 1), (0, 2), (2, 1)])

    def test_graph_api_contract(self):
        graph = DiGraph()
        graph.add_edge("b", "a")
        graph.add_edge("b", "a")
        graph.add_edge("b", "c")
        self.assertEqual(graph.nodes(), ["a", "b", "c"])
        self.assertEqual(graph.successors("b"), ["a", "c"])
        self.assertEqual(graph.successors("a"), [])
        self.assertEqual(graph.edge_count(), 2)
        self.assertTrue(graph.has_edge("b", "a"))
        self.assertFalse(graph.has_edge("a", "b"))
        self.assertFalse(graph.has_edge("zzz", "a"))
        self.assertIsNot(graph.successors("b"), graph.successors("b"))
        with self.assertRaises(KeyError):
            graph.successors("missing")

    def test_validation_is_atomic(self):
        graph = DiGraph()
        with self.assertRaises(TypeError):
            graph.add_edge("a", 3)
        with self.assertRaises(ValueError):
            graph.add_edge("a", "")
        with self.assertRaises(TypeError):
            graph.add_node(None)
        with self.assertRaises(ValueError):
            graph.add_node("")
        self.assertEqual(graph.nodes(), [])
        self.assertEqual(graph.edge_count(), 0)

    def test_self_loop_registered_and_counted(self):
        graph = build([("z", "z")])
        self.assertTrue(graph.has_edge("z", "z"))
        self.assertEqual(graph.edge_count(), 1)
        self.assertEqual(cyclic_components(graph), [["z"]])
        self.assertEqual(condensation_edges(graph), [])
        mixed = build([("a", "b")], extra=["c"])
        self.assertEqual(cyclic_components(mixed), [])

    def test_condensation_edges_are_unique_and_sorted(self):
        graph = build([("a", "b"), ("b", "a"), ("a", "c"), ("b", "c"), ("c", "d"), ("c", "e"), ("d", "e")])
        self.assertEqual(components(graph), [["a", "b"], ["c"], ["d"], ["e"]])
        self.assertEqual(condensation_edges(graph), [(0, 1), (1, 2), (1, 3), (2, 3)])

    def test_component_order_follows_smallest_member(self):
        graph = build([("m", "n"), ("n", "m"), ("b", "z"), ("z", "b"), ("c", "m")])
        self.assertEqual(components(graph), [["b", "z"], ["c"], ["m", "n"]])
        self.assertEqual(condensation_edges(graph), [(1, 2)])

    def test_long_path_does_not_hit_recursion_limit(self):
        edges = [("n%05d" % i, "n%05d" % (i + 1)) for i in range(6000)]
        edges.append(("n06000", "n00000"))
        graph = build(edges)
        found = components(graph)
        self.assertEqual(len(found), 1)
        self.assertEqual(len(found[0]), 6001)

    def test_matches_reachability_definition_on_fixed_graphs(self):
        for edges in GRAPH_FIXTURES:
            graph = build(edges, extra=NAMES[:2])
            reach = {node: reachable(graph, node) for node in graph.nodes()}
            expected = []
            for node in graph.nodes():
                group = sorted(other for other in graph.nodes() if other in reach[node] and node in reach[other])
                if group not in expected:
                    expected.append(group)
            expected.sort(key=lambda group: group[0])
            self.assertEqual(components(graph), expected)
            cyc = [g for g in expected if len(g) > 1 or graph.has_edge(g[0], g[0])]
            self.assertEqual(cyclic_components(graph), cyc)
            self.assertEqual(is_acyclic(graph), not cyc)


if __name__ == "__main__":
    unittest.main()
