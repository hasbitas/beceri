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
    def test_empty_and_isolated(self):
        self.assertEqual(solution.components(0, []), [])
        self.assertEqual(solution.components(1, ()), [[0]])
        self.assertEqual(solution.components(5, iter(())), [[0], [1], [2], [3], [4]])


    def test_bridge_and_order_independence(self):
        edges = [(0, 1), (2, 3), (0, 2)]
        for perm in itertools.permutations(edges):
            for flips in itertools.product((False, True), repeat=len(edges)):
                candidate = [edge[::-1] if flip else edge
                             for edge, flip in zip(perm, flips)]
                with self.subTest(edges=candidate):
                    self.assertEqual(solution.components(5, candidate),
                                     [[0, 1, 2, 3], [4]])

    def test_loops_duplicates_and_cycles(self):
        edges = [(4, 4), (0, 1), (1, 2), (2, 0), (1, 0),
                 (0, 1), (3, 3), (4, 4)]
        self.assertEqual(solution.components(5, edges), [[0, 1, 2], [3], [4]])




    def test_n_validation_and_precedence(self):
        for n in (True, False, 2.0, '2', None, IntSubclass(2)):
            with self.subTest(n=n), self.assertRaises(TypeError):
                solution.components(n, None)
        for n in (-1, -20):
            with self.subTest(n=n), self.assertRaises(ValueError):
                solution.components(n, None)
        for edges in (None, 42, 3.5, True):
            with self.subTest(edges=edges), self.assertRaises(TypeError):
                solution.components(0, edges)

    def test_edge_validation(self):
        for edge in (None, 42, '01', {0, 1}, {0: 1}, iter([0, 1])):
            with self.subTest(edge=edge), self.assertRaises(TypeError):
                solution.components(3, [edge])
        for edge in ([], (), [0], (0, 1, 2), [None]):
            with self.subTest(edge=edge), self.assertRaises(ValueError):
                solution.components(3, [edge])
        for value in (True, False, 1.0, '1', None, IntSubclass(1)):
            for edge in ((value, 0), (0, value), (-1, value)):
                with self.subTest(edge=edge), self.assertRaises(TypeError):
                    solution.components(3, [edge])
        for edge in ((-1, 0), (0, -1), (3, 0), (0, 3), (100, 100)):
            with self.subTest(edge=edge), self.assertRaises(ValueError):
                solution.components(3, [edge])
        with self.assertRaises(ValueError):
            solution.components(0, [(0, 0)])

    def test_late_validation_and_first_invalid_edge(self):
        stream = SinglePass([(0, 1), (1, 2), (0, 2), (True, 0), (3, 0)])
        with self.assertRaises(TypeError):
            solution.components(3, stream)
        self.assertEqual(len(stream.seen), 4)
        with self.assertRaises(ValueError):
            solution.components(3, [(0, 1), (3, 0), None])
        with self.assertRaises(TypeError):
            solution.components(0, [None])

    def test_no_mutation_and_fresh_results(self):
        edges = [[3, 2], [1, 0], [0, 0]]
        original = [edge[:] for edge in edges]
        a = solution.components(5, edges)
        b = solution.components(5, edges)
        expected = [[0, 1], [2, 3], [4]]
        self.assertEqual(a, expected)
        self.assertEqual(b, expected)
        self.assertIs(type(a), list)
        self.assertIsNot(a, b)
        for i, group in enumerate(a):
            self.assertIs(type(group), list)
            for other in a[i + 1:] + b + edges:
                self.assertIsNot(group, other)
        a[0].append(99)
        a.append([100])
        self.assertEqual(b, expected)
        self.assertEqual(edges, original)
        bad = [[1, 0], [2, 3], [0, -1]]
        saved = [edge[:] for edge in bad]
        with self.assertRaises(ValueError):
            solution.components(5, bad)
        self.assertEqual(bad, saved)
        self.assertIsNot(solution.components(0, []), solution.components(0, []))


if __name__ == '__main__':
    unittest.main()
