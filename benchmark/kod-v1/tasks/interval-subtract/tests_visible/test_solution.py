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




    def test_empty_holes_do_not_split(self):
        self.check((0, 10), [(5, 5), (0, 0), (10, 10), (-1, -1)],
                   [(0, 10)])

    def test_touching_overlapping_and_duplicate_holes(self):
        self.check((0, 12), [(6, 9), (2, 4), (4, 6), (2, 4)],
                   [(0, 2), (9, 12)])
        self.check((0, 12), [(2, 7), (5, 9)], [(0, 2), (9, 12)])
        self.check((0, 12), [(0, 5), (5, 12)], [])


    def test_negative_and_large_exact_endpoints(self):
        self.check((-20, -2), [(-17, -12), (-8, -4)],
                   [(-20, -17), (-12, -8), (-4, -2)])
        n = 10 ** 100
        self.check((n, n + 10), [(n + 1, n + 2), (n + 8, n + 9)],
                   [(n, n + 1), (n + 2, n + 8), (n + 9, n + 10)])
        self.check((-n, n), [(-n + 1, n - 1)],
                   [(-n, -n + 1), (n - 1, n)])


    def test_inputs_unchanged_and_calls_independent(self):
        base = [0, 10]
        holes = [[7, 9], [2, 5], [3, 4]]
        expected = [(0, 2), (5, 7), (9, 10)]
        self.check(base, holes, expected)
        self.assertEqual(base, [0, 10])
        self.assertEqual(holes, [[7, 9], [2, 5], [3, 4]])
        self.check((0, 10), [], [(0, 10)])
        self.check(base, holes, expected)
        result = solution.subtract(base, holes)
        result.append((100, 101))
        self.check(base, holes, expected)



if __name__ == '__main__':
    unittest.main()
