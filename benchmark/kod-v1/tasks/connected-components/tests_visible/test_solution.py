import itertools
import unittest

import solution


class IntSubclass(int):
    pass


class ListSubclass(list):
    pass


class TupleSubclass(tuple):
    pass


class SinglePass:
    def __init__(self, values):
        self.values = values
        self.started = False
        self.seen = []

    def __iter__(self):
        if self.started:
            raise AssertionError('iterated twice')
        self.started = True
        for value in self.values:
            self.seen.append(value)
            yield value


def oracle(n, edges):
    # Boolean transitive closure, independent of union-find.
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v in edges:
        reach[u][v] = reach[v][u] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    remaining = set(range(n))
    groups = []
    while remaining:
        first = min(remaining)
        group = [j for j in range(n) if reach[first][j]]
        groups.append(group)
        remaining.difference_update(group)
    return sorted(groups, key=lambda group: (-len(group), group[0]))


class ComponentsTests(unittest.TestCase):

    def test_canonical_size_and_ties(self):
        edges = [(7, 8), (6, 4), (2, 0), (9, 8), (4, 5), (3, 1)]
        self.assertEqual(solution.components(11, edges),
                         [[4, 5, 6], [7, 8, 9], [0, 2], [1, 3], [10]])



    def test_all_small_graphs(self):
        for n in range(5):
            possible = list(itertools.combinations(range(n), 2))
            for mask in range(1 << len(possible)):
                edges = [edge for i, edge in enumerate(possible) if mask & (1 << i)]
                expected = oracle(n, edges)
                for candidate in (edges, [(v, u) for u, v in reversed(edges)]):
                    with self.subTest(n=n, edges=candidate):
                        self.assertEqual(solution.components(n, candidate), expected)

    def test_single_pass_and_edge_container_subclasses(self):
        edges = [ListSubclass([3, 1]), TupleSubclass((1, 2)), [0, 0], (2, 3)]
        stream = SinglePass(edges)
        self.assertEqual(solution.components(5, stream), [[1, 2, 3], [0], [4]])
        self.assertEqual(stream.seen, edges)
        self.assertEqual(solution.components(2, ((i, i) for i in range(2))), [[0], [1]])

    def test_long_chains(self):
        n = 5000
        for edges in ([(i, i + 1) for i in range(n - 1)],
                      [(i + 1, i) for i in range(n - 1)]):
            self.assertEqual(solution.components(n, edges), [list(range(n))])






if __name__ == '__main__':
    unittest.main()
