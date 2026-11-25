import unittest

import solution


class SubtractTests(unittest.TestCase):
    def check(self, base, holes, expected):
        result = solution.subtract(base, holes)
        self.assertIsInstance(result, list)
        self.assertEqual(result, expected)
        for piece in result:
            self.assertIsInstance(piece, tuple)
            self.assertEqual(len(piece), 2)
            self.assertTrue(all(isinstance(endpoint, int) for endpoint in piece))
            self.assertLess(piece[0], piece[1])
        for first, second in zip(result, result[1:]):
            self.assertLess(first[1], second[0])

    def test_no_holes_and_empty_base(self):
        self.check((-4, 9), [], [(-4, 9)])
        self.check((3, 3), [], [])
        self.check((3, 3), [(-100, 100)], [])

    def test_unsorted_disjoint_holes(self):
        self.check((0, 20), [(12, 15), (2, 4), (7, 9)],
                   [(0, 2), (4, 7), (9, 12), (15, 20)])

    def test_clipping_and_outside_intervals(self):
        self.check((0, 10), [(12, 20), (-8, -1), (-2, 3), (8, 11)],
                   [(3, 8)])
        self.check((0, 10), [(-1, 11)], [])
        self.check((0, 10), [(-4, 0), (10, 14)], [(0, 10)])



    def test_nested_holes(self):
        self.check((0, 15), [(2, 12), (4, 6), (8, 9)],
                   [(0, 2), (12, 15)])
        self.check((0, 15), [(2, 12), (2, 5), (3, 4)],
                   [(0, 2), (12, 15)])
        self.check((0, 15), [(-10, 100), (3, 4), (6, 8)], [])


    def test_iterator_input(self):
        holes = ([a, b] for a, b in [(7, 9), (2, 5), (3, 4)])
        self.check([0, 10], holes, [(0, 2), (5, 7), (9, 10)])


    def test_small_exhaustive_pairs(self):
        intervals = [(a, b) for a in range(-2, 5) for b in range(a, 5)]
        for first in intervals:
            for second in intervals:
                holes = [first, second]
                remaining = [x for x in range(3)
                             if not any(a <= x < b for a, b in holes)]
                expected = []
                for x in remaining:
                    if expected and expected[-1][1] == x:
                        expected[-1] = (expected[-1][0], x + 1)
                    else:
                        expected.append((x, x + 1))
                with self.subTest(holes=holes):
                    self.check((0, 3), holes, expected)


if __name__ == '__main__':
    unittest.main()
