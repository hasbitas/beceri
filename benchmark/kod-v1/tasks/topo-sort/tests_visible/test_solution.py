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


    def test_newly_eligible_competes_with_existing(self):
        self.assertEqual(solution.topo_sort({'b': ['a'], 'z': []}),
                         ['b', 'a', 'z'])
        self.assertEqual(solution.topo_sort({'c': ['b'], 'b': ['a'], 'z': []}),
                         ['c', 'b', 'a', 'z'])

    def test_targets_duplicates_and_multiple_predecessors(self):
        graph = {'c': ['d', 'd'], 'b': ('d', 'd'), 'a': {'b', 'c'}}
        self.assertEqual(solution.topo_sort(graph), ['a', 'b', 'c', 'd'])
        self.assertEqual(solution.topo_sort({'x': ['y', 'y']}), ['x', 'y'])
        self.assertEqual(solution.topo_sort({'only': []}), ['only'])



    def test_cycles(self):
        for graph in ({'a': ['a']}, {'a': ['b'], 'b': ['a']},
                      {'a': ['b'], 'b': ['c'], 'c': ['a']},
                      {'free': [], 'x': ['y'], 'y': ['x']},
                      {'a': ['a', 'a']}):
            with self.subTest(graph=graph):
                self.assert_cycle(graph)


    def test_nonmutation_and_shared_neighbors(self):
        shared = ['c', 'b', 'b']
        graph = {'a': shared, 'z': shared, 'b': ('c',), 'c': set()}
        before = copy.deepcopy(graph)
        self.assertEqual(solution.topo_sort(graph), ['a', 'z', 'b', 'c'])
        self.assertEqual(graph, before)
        self.assertIs(graph['a'], shared)
        self.assertIs(graph['z'], shared)
        shared_cycle = ['a']
        graph = {'a': shared_cycle, 'b': shared_cycle}
        self.assert_cycle(graph)
        self.assertIs(graph['a'], shared_cycle)



if __name__ == '__main__':
    unittest.main()
