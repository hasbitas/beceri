import itertools
import math
import unittest
from decimal import Decimal
from fractions import Fraction

import solution


class HistogramTests(unittest.TestCase):

    def test_single_bin_and_empty(self):
        self.assertEqual(solution.histogram([-1, 0, 0.5, 1, 2], 1, 0, 1), [3])
        self.assertEqual(solution.histogram([], 3, -10, 10), [0, 0, 0])
        self.assertEqual(solution.histogram([11, -11], 3, -10, 10), [0, 0, 0])


    def test_one_pass_iterator(self):
        items = iter([0, 1, 2, 3, 4])
        self.assertEqual(solution.histogram(items, 2, 0, 4), [2, 3])
        self.assertEqual(list(items), [])
        self.assertEqual(solution.histogram((x for x in [0.25, 0.75]), 2, 0, 1), [1, 1])


    def test_arbitrary_size_integers(self):
        base = 10 ** 400
        self.assertEqual(solution.histogram([base - 1, base, base + 1, base + 2, base + 3, base + 4, base + 5], 2, base, base + 4), [2, 3])



    def test_invalid_bounds(self):
        for bad in [True, None, '0', complex(0), Decimal('0'), Fraction(0)]:
            for low, high in [(bad, 1), (0, bad)]:
                with self.subTest(low=low, high=high), self.assertRaises(TypeError):
                    solution.histogram([], 2, low, high)
        for bad in [math.nan, math.inf, -math.inf]:
            for low, high in [(bad, 1), (0, bad)]:
                with self.subTest(low=low, high=high), self.assertRaises(ValueError):
                    solution.histogram([], 2, low, high)
        for low, high in [(1, 1), (2, 1), (-0.0, 0.0)]:
            with self.subTest(low=low, high=high), self.assertRaises(ValueError):
                solution.histogram([], 2, low, high)




if __name__ == '__main__':
    unittest.main()
