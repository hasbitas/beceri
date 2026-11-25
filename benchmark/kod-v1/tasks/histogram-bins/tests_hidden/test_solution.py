import itertools
import math
import unittest
from decimal import Decimal
from fractions import Fraction

import solution


class HistogramTests(unittest.TestCase):
    def test_edges_repeats_and_outliers(self):
        data = [9, -1, 8, 6, 4, 2, 0, 2, 8, 1, 7]
        self.assertEqual(solution.histogram(data, 4, 0, 8), [2, 2, 1, 4])
        self.assertEqual(solution.histogram([-3, -2, -1, 0, 1, 2, 3], 4, -2, 2), [1, 1, 1, 2])


    def test_fresh_output_and_input_preservation(self):
        data = [3, 1, 2, 0, 4]
        before = data[:]
        first = solution.histogram(data, 2, 0, 4)
        second = solution.histogram(data, 2, 0, 4)
        self.assertEqual(data, before)
        self.assertIsNot(first, second)
        first[0] = 100
        self.assertEqual(second, [2, 3])
        self.assertTrue(all(type(x) is int for x in second))
        self.assertIs(type(second), list)


    def test_exact_float_boundaries(self):
        edge = 0.5
        values = [math.nextafter(edge, -math.inf), edge, math.nextafter(edge, math.inf)]
        self.assertEqual(solution.histogram(values, 2, 0, 1), [1, 2])
        # The stored binary value of 0.3 is below the exact value 3/10.
        self.assertEqual(solution.histogram([0.3, math.nextafter(0.3, math.inf)], 10, 0, 1), [0, 0, 1, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual(solution.histogram([-1e308, 0, 1e308], 2, -1e308, 1e308), [1, 2])
        tiny = math.ulp(0.0)
        self.assertEqual(solution.histogram([0.0, tiny, tiny * 2], 2, 0.0, tiny * 2), [1, 2])


    def test_bounded_independent_interval_oracle(self):
        for low, span, bins in itertools.product([-3, 0, 2], [1, 3, 6], [1, 2, 3, 5]):
            high = low + span
            values = [n / 4 for n in range((low - 1) * 4, (high + 1) * 4 + 1)]
            expected = []
            for i in range(bins):
                left = Fraction(low) + Fraction(span * i, bins)
                right = Fraction(low) + Fraction(span * (i + 1), bins)
                expected.append(sum(left <= Fraction(v) and (Fraction(v) <= right if i == bins - 1 else Fraction(v) < right) for v in values))
            with self.subTest(low=low, span=span, bins=bins):
                self.assertEqual(solution.histogram(reversed(values), bins, low, high), expected)

    def test_invalid_bins(self):
        for bins in [True, False, 2.0, '2', None, Fraction(2)]:
            with self.subTest(bins=bins), self.assertRaises(TypeError):
                solution.histogram([], bins, 0, 1)
        for bins in [0, -1, -100]:
            with self.subTest(bins=bins), self.assertRaises(ValueError):
                solution.histogram([], bins, 0, 1)


    def test_invalid_values(self):
        for data in [None, 42, 1.2]:
            with self.subTest(data=data), self.assertRaises(TypeError):
                solution.histogram(data, 2, 0, 1)
        for bad in [True, False, None, '0.5', complex(1), Decimal('1'), Fraction(1)]:
            data = [0.5, bad, 1]
            before = data[:]
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                solution.histogram(data, 2, 0, 1)
            self.assertEqual(data, before)
        for bad in [math.nan, math.inf, -math.inf]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                solution.histogram([0, bad], 2, 0, 1)

    def test_validation_order(self):
        def untouched():
            raise AssertionError('values consumed before parameter validation')
            yield 0
        cases = [
            (True, None, None, TypeError),
            (0, None, None, ValueError),
            (2, math.inf, None, ValueError),
            (2, 1, None, TypeError),
            (2, 2, 1, ValueError),
        ]
        for bins, low, high, error in cases:
            with self.subTest(bins=bins, low=low, high=high), self.assertRaises(error):
                solution.histogram(untouched(), bins, low, high)
        with self.assertRaises(TypeError):
            solution.histogram([None, math.inf], 2, 0, 1)
        with self.assertRaises(ValueError):
            solution.histogram([math.inf, None], 2, 0, 1)


if __name__ == '__main__':
    unittest.main()
