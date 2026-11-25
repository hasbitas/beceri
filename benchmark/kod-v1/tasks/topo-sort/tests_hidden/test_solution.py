import copy
import itertools
import unittest

import solution


class TestTopoSort(unittest.TestCase):
    def assert_cycle(self, graph):
        before = copy.deepcopy(graph)
        with self.assertRaises(ValueError) as caught:
            solution.topo_sort(graph)
        self.assertEqual(str(caught.exception), 'graph contains a cycle')
        self.assertEqual(graph, before)

    def test_empty_and_fresh_output(self):
        graph = {}
        first = solution.topo_sort(graph)
        second = solution.topo_sort(graph)
        self.assertIs(type(first), list)
        self.assertEqual(first, [])
        self.assertIsNot(first, second)
        graph = {'a': [], 'b': []}
        output = solution.topo_sort(graph)
        self.assertIs(type(output), list)
        self.assertEqual(output, ['a', 'b'])
        output.append('extra')
        self.assertEqual(solution.topo_sort(graph), ['a', 'b'])



    def test_unicode_and_empty_labels(self):
        graph = {'é': [], 'Z': [], 'a': [], '': [], 'e\u0301': [], 'ß': []}
        self.assertEqual(solution.topo_sort(graph), ['', 'Z', 'a', 'e\u0301', 'ß', 'é'])
        self.assertEqual(solution.topo_sort({'z': [''], 'é': []}), ['z', '', 'é'])

    def test_input_order_and_container_independence(self):
        entries = [('m', ['b', 'a']), ('z', []), ('b', ['c']), ('a', [])]
        for ordering in itertools.permutations(entries):
            for container in (list, tuple, set):
                graph = {key: container(reversed(value)) for key, value in ordering}
                with self.subTest(order=tuple(graph), container=container):
                    self.assertEqual(solution.topo_sort(graph), ['m', 'a', 'b', 'c', 'z'])


    def test_invalid_types_and_validation_before_cycles(self):
        class DictSubclass(dict):
            pass
        class StrSubclass(str):
            pass
        class ListSubclass(list):
            pass
        class TupleSubclass(tuple):
            pass
        class SetSubclass(set):
            pass
        bad = [None, [], (), 'abc', DictSubclass(), {1: []},
               {StrSubclass('a'): []}, {'a': 'bc'}, {'a': None},
               {'a': {}}, {'a': frozenset()}, {'a': [1]},
               {'a': (False,)}, {'a': {None}},
               {'a': [StrSubclass('b')]}, {'a': ListSubclass()},
               {'a': TupleSubclass()}, {'a': SetSubclass()},
               {'cycle': ['cycle'], 'z': [None]}]
        for graph in bad:
            with self.subTest(graph=graph):
                before = copy.deepcopy(graph)
                with self.assertRaises(TypeError):
                    solution.topo_sort(graph)
                self.assertEqual(graph, before)


    def test_all_three_vertex_directed_graphs(self):
        nodes = ('a', 'b', 'c')
        edges = tuple(itertools.product(nodes, repeat=2))
        orders = tuple(itertools.permutations(nodes))
        for mask in range(1 << len(edges)):
            selected = [edge for i, edge in enumerate(edges) if mask & (1 << i)]
            valid = [order for order in orders
                     if all(order.index(a) < order.index(b) for a, b in selected)]
            graph = {node: [b for a, b in reversed(selected) if a == node]
                     for node in reversed(nodes)}
            with self.subTest(mask=mask):
                if valid:
                    self.assertEqual(solution.topo_sort(graph), list(min(valid)))
                else:
                    self.assert_cycle(graph)


if __name__ == '__main__':
    unittest.main()
