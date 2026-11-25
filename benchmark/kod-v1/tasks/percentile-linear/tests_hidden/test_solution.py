import itertools
import math
import unittest
from decimal import Decimal
from fractions import Fraction

import solution


class IntSubclass(int):
    pass


class FloatSubclass(float):
    pass


class ListSubclass(list):
    pass


class TupleSubclass(tuple):
    pass


class PercentileTests(unittest.TestCase):
    def check_result(self, values, p, expected):
        result = solution.percentile(values, p)
        self.assertIs(type(result), float)
        self.assertAlmostEqual(result, expected)

    def test_interpolation(self):
        for p, expected in [(0, 0), (10, 3), (25, 7.5), (50, 15),
                            (75, 22.5), (90, 27), (100, 30)]:
            with self.subTest(p=p):
                self.check_result([30, 0, 20, 10], p, expected)
        self.check_result([100, -20], 12.5, -5)
        self.check_result([1.5, -2.5, 7.5], 25, -0.5)

    def test_exact_interior_ranks(self):
        for p, expected in [(25, 4), (50, 9), (75, 16)]:
            with self.subTest(p=p):
                self.check_result([25, 9, 1, 16, 4], p, expected)

    def test_duplicates(self):
        for p, expected in [(25, 2), (50, 2), (75, 4), (100, 10)]:
            with self.subTest(p=p):
                self.check_result([2, 10, 2, 2], p, expected)
        self.check_result([7, 7, 7], 37.1, 7)





    def test_invalid_numerical_values(self):
        for item in [float('nan'), float('inf'), -float('inf'), 10 ** 400]:
            with self.subTest(item=repr(item)):
                with self.assertRaises(ValueError):
                    solution.percentile([1], item)
                for p in [0, 50, 100]:
                    with self.assertRaises(ValueError):
                        solution.percentile([1, item], p)
                with self.assertRaises(ValueError):
                    solution.percentile([item], 25)
        for p in [-1, -0.0001, 100.0001, 101]:
            with self.assertRaises(ValueError):
                solution.percentile([1], p)


    def test_preservation(self):
        values = [9, 1, 4, 1]
        original = values[:]
        solution.percentile(values, 35)
        self.assertEqual(values, original)
        marker = object()
        values = [9, 1, marker]
        with self.assertRaises(TypeError):
            solution.percentile(values, 50)
        self.assertEqual(values, [9, 1, marker])

    def test_large_finite_interpolation(self):
        for p, expected in [(25, -5e307), (50, 0.0), (75, 5e307)]:
            with self.subTest(p=p):
                result = solution.percentile([-1e308, 1e308], p)
                self.assertIs(type(result), float)
                self.assertTrue(math.isfinite(result))
                self.assertTrue(math.isclose(result, expected, rel_tol=1e-14))
        self.assertEqual(solution.percentile([1e308, 1e308], 50), 1e308)

    def test_affine_sample_grid(self):
        # In an arithmetic progression the interpolated quantile is affine in p.
        for n in range(2, 9):
            values = [float(-12 + 4 * i) for i in range(n)]
            for p in [0, 1, 12.5, 33.25, 50, 66.5, 87.5, 99, 100]:
                with self.subTest(n=n, p=p):
                    self.check_result(values[::-1], p, -12 + 4 * (n - 1) * p / 100)


if __name__ == '__main__':
    unittest.main()
