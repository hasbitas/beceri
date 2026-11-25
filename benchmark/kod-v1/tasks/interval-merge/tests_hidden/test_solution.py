import copy
import itertools
import unittest

import solution


class MergeTests(unittest.TestCase):
    def assert_merge(self, intervals, expected):
        before = copy.deepcopy(intervals)
        actual = solution.merge(intervals)
        self.assertEqual(actual, expected)
        self.assertIs(type(actual), list)
        self.assertIsNot(actual, intervals)
        for item in actual:
            self.assertIs(type(item), list)
            for original in intervals:
                self.assertIsNot(item, original)
        self.assertEqual(len({id(item) for item in actual}), len(actual))
        self.assertEqual(intervals, before)
        return actual



    def test_all_permutations_of_bridge(self):
        intervals = [(0, 2), (5, 9), (2, 5), (20, 20)]
        for permutation in itertools.permutations(intervals):
            with self.subTest(permutation=permutation):
                self.assert_merge(permutation, [[0, 9], [20, 20]])



    def test_singletons_and_mixed_containers(self):
        self.assert_merge(((7, 7), [0, 0], (7, 7), [10, 12], (12, 12)),
                          [[0, 0], [7, 7], [10, 12]])

    def test_arbitrarily_large_integers(self):
        huge = 10 ** 120
        self.assert_merge([[huge, huge + 2], [-huge, -huge],
                           [huge + 2, huge + 8], [huge + 9, huge + 10]],
                          [[-huge, -huge], [huge, huge + 8],
                           [huge + 9, huge + 10]])



    def test_invalid_item_containers(self):
        for item in (None, 3, '12', {0: 1, 1: 2}, {1, 2}):
            with self.subTest(item=item):
                with self.assertRaises(TypeError):
                    solution.merge([[0, 100], item])

    def test_invalid_lengths(self):
        for item in ([], (), [1], [1, 2, 3], (None, None, None)):
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    solution.merge([item])

    def test_invalid_endpoint_types(self):
        for value in (False, True, 1.0, '1', None, [], complex(1, 0)):
            for item in ([value, 10], [-10, value]):
                with self.subTest(item=item):
                    with self.assertRaises(TypeError):
                        solution.merge([item])

    def test_reversed_intervals_even_if_contained(self):
        for intervals in ([[4, 3]], [[0, 100], [8, 2]],
                          [(5, 5), (-1, -2)]):
            with self.subTest(intervals=intervals):
                before = copy.deepcopy(intervals)
                with self.assertRaises(ValueError):
                    solution.merge(intervals)
                self.assertEqual(intervals, before)

    def test_validation_order_and_no_mutation_on_failure(self):
        cases = [
            ([[9, 8], None], ValueError),
            ([None, [9, 8]], TypeError),
            ([[False], [0, 1]], ValueError),
            ([[5, 'x']], TypeError),
            ([[0, 100], [True, 2]], TypeError),
            ([[8, 9], [0, 1], [None, 2]], TypeError),
        ]
        for intervals, error in cases:
            with self.subTest(intervals=intervals):
                before = copy.deepcopy(intervals)
                with self.assertRaises(error):
                    solution.merge(intervals)
                self.assertEqual(intervals, before)


if __name__ == '__main__':
    unittest.main()
