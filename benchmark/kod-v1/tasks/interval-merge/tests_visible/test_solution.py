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

    def test_empty_inputs_and_fresh_results(self):
        first = self.assert_merge([], [])
        second = self.assert_merge((), [])
        self.assertIsNot(first, second)

    def test_unordered_transitive_endpoint_chain(self):
        self.assert_merge([[8, 10], [2, 4], [4, 8], [-5, -2]],
                          [[-5, -2], [2, 10]])


    def test_integer_adjacency_is_not_endpoint_touching(self):
        self.assert_merge([[3, 4], [1, 2]], [[1, 2], [3, 4]])
        self.assert_merge([[-2, -1], [0, 0], [1, 1]],
                          [[-2, -1], [0, 0], [1, 1]])

    def test_containment_duplicates_and_equal_starts(self):
        self.assert_merge([[1, 3], [1, 20], [8, 8], [1, 3],
                           [15, 16], [20, 25], [-10, -5]],
                          [[-10, -5], [1, 25]])



    def test_returned_items_are_independent_of_input_and_each_other(self):
        intervals = [[8, 10], [0, 2]]
        result = self.assert_merge(intervals, [[0, 2], [8, 10]])
        result[0][0] = -100
        self.assertEqual(result[1], [8, 10])
        self.assertEqual(intervals, [[8, 10], [0, 2]])
        again = self.assert_merge(intervals, [[0, 2], [8, 10]])
        self.assertIsNot(result, again)
        self.assertIsNot(result[1], again[1])

    def test_invalid_outer_types(self):
        for value in (None, 1, True, '12', {1: 2}, {1, 2}, iter(())):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.merge(value)







if __name__ == '__main__':
    unittest.main()
