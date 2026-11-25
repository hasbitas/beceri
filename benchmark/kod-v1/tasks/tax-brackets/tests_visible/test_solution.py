import copy
import itertools
import unittest
from fractions import Fraction

import solution


class IntSubclass(int):
    pass


class TaxTests(unittest.TestCase):
    def check_tax(self, income, brackets, expected):
        before = copy.deepcopy(brackets)
        result = solution.tax(income, brackets)
        self.assertIs(type(result), int)
        self.assertEqual(result, expected)
        self.assertEqual(brackets, before)


    def test_each_bracket_is_rounded_separately(self):
        self.check_tax(2, [(1, 5000), (None, 5000)], 2)
        self.check_tax(3, [(1, 3333), (2, 3333), (None, 3333)], 0)
        self.check_tax(4, [(1, 6000), (2, 6000), (None, 2000)], 2)


    def test_boundaries_and_decreasing_rates(self):
        schedule = [[10, 10000], (20, 0), [None, 5000]]
        for income, expected in [(9, 9), (10, 10), (11, 10),
                                 (19, 10), (20, 10), (21, 11),
                                 (22, 11), (23, 12)]:
            with self.subTest(income=income):
                self.check_tax(income, schedule, expected)

    def test_unbounded_integer_arithmetic(self):
        huge = 10 ** 100
        self.check_tax(huge + 1, [(None, 5000)], huge // 2 + 1)
        self.check_tax(huge + 3, [(huge, 10000), (None, 5000)], huge + 2)
        self.check_tax(huge + 11, [(huge, 0), (None, 10000)], 11)





    def test_late_invalid_rates_are_not_skipped(self):
        for income in (0, 1, 10):
            for rate in (True, 2.0, '5000', None, IntSubclass(2), -1, 10001):
                with self.subTest(income=income, rate=rate):
                    schedule = [[100, 0], [None, rate]]
                    before = copy.deepcopy(schedule)
                    error = TypeError if type(rate) is not int else ValueError
                    with self.assertRaises(error):
                        solution.tax(income, schedule)
                    self.assertEqual(schedule, before)



if __name__ == '__main__':
    unittest.main()
