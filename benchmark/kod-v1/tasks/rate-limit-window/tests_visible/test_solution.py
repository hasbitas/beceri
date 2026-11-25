import unittest
from itertools import combinations_with_replacement

import solution


class AllowedTests(unittest.TestCase):
    def check(self, timestamps, limit, window, expected):
        before = timestamps[:]
        result = solution.allowed(timestamps, limit, window)
        self.assertIsInstance(result, list)
        self.assertEqual(result, expected)
        self.assertTrue(all(type(item) is bool for item in result))
        self.assertEqual(timestamps, before)



    def test_duplicates_in_order(self):
        self.check([3, 3, 3, 3, 8, 8, 8], 2, 5,
                   [True, True, False, False, True, True, False])
        self.check([0, 0, 0], 1, 10, [True, False, False])


    def test_expire_multiple_and_long_gaps(self):
        self.check([0, 1, 2, 3, 100, 100, 100, 100], 3, 10,
                   [True, True, True, False, True, True, True, False])


    def test_calls_are_independent_and_results_fresh(self):
        stamps = [1, 1, 2]
        first = solution.allowed(stamps, 1, 10)
        second = solution.allowed(stamps, 1, 10)
        self.assertIsNot(first, second)
        self.assertEqual(first, [True, False, False])
        self.assertEqual(second, first)
        first.append(False)
        self.check(stamps, 5, 10, [True, True, True])

    def test_invalid_parameters_even_for_empty_input(self):
        for bad in [-1, True, False, 1.0, '1', None, [], {}]:
            with self.subTest(limit=bad):
                with self.assertRaises(ValueError):
                    solution.allowed([], bad, 1)
        for bad in [-1, 0, True, False, 1.0, '1', None, [], {}]:
            with self.subTest(window=bad):
                with self.assertRaises(ValueError):
                    solution.allowed([], 0, bad)





if __name__ == '__main__':
    unittest.main()
