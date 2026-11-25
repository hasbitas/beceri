import itertools
import unittest

import solution


class Integer(int):
    pass


class ListSubclass(list):
    pass


class TupleSubclass(tuple):
    pass


class WindowMaxTests(unittest.TestCase):
    def test_typical_windows(self):
        self.assertEqual(solution.window_max([1, 3, -1, -3, 5, 3, 6, 7], 3),
                         [3, 3, 5, 5, 6, 7])
        self.assertEqual(solution.window_max((8, 2, 4, 1, 0), 2), [8, 4, 4, 1])

    def test_decreasing_and_negative(self):
        self.assertEqual(solution.window_max([9, 8, 7, 6, 5], 3), [9, 8, 7])
        self.assertEqual(solution.window_max([-2, -8, -5, -9], 2), [-2, -5, -5])

    def test_duplicate_maxima(self):
        self.assertEqual(solution.window_max([7, 7, 1, 0, 7, 7, -1], 2),
                         [7, 7, 1, 7, 7, 7])
        self.assertEqual(solution.window_max([4] * 12, 5), [4] * 8)

    def test_window_boundaries_and_empty(self):
        for values in ([], (), [3], (3,), [5, 1, 9, -2]):
            with self.subTest(values=values):
                self.assertEqual(solution.window_max(values, 1), list(values))
                self.assertEqual(solution.window_max(values, len(values) + 1), [])
                self.assertEqual(solution.window_max(values, 10 ** 100), [])
                if values:
                    self.assertEqual(solution.window_max(values, len(values)), [max(values)])

    def test_exact_large_integers(self):
        huge = 10 ** 400
        values = [huge + 1, huge, -huge, -huge - 1, huge + 2]
        self.assertEqual(solution.window_max(values, 2),
                         [huge + 1, huge, -huge, huge + 2])





    def test_invalid_elements_even_without_windows(self):
        for bad in (True, False, 1.0, None, '3', [], {}, complex(1)):
            for values in ([bad, 2], [2, bad], (2, bad)):
                for k in (1, 2, 5):
                    with self.subTest(bad=bad, values=values, k=k):
                        with self.assertRaises(TypeError):
                            solution.window_max(values, k)


    def test_no_mutation_and_fresh_outputs(self):
        for values in ([], [8, 2, 5, 1]):
            for k in (1, 2, 20):
                original = values[:]
                first = solution.window_max(values, k)
                second = solution.window_max(values, k)
                self.assertIs(type(first), list)
                self.assertIsNot(first, values)
                self.assertIsNot(first, second)
                first.append(999)
                self.assertEqual(values, original)
        values = [3, 2, None, 1]
        original = values[:]
        for k in (2, 10, 0, False):
            with self.assertRaises((TypeError, ValueError)):
                solution.window_max(values, k)
            self.assertEqual(values, original)


    def test_long_inputs(self):
        values = list(range(12000, 0, -1))
        self.assertEqual(solution.window_max(values, 6000), list(range(12000, 5999, -1)))


if __name__ == '__main__':
    unittest.main()
