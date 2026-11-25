import itertools
import math
import unittest
from decimal import Decimal
from fractions import Fraction

import solution


class PickTests(unittest.TestCase):
    def check_pick(self, weights, r, expected):
        before = weights[:]
        result = solution.pick(weights, r)
        self.assertIs(type(result), int)
        self.assertEqual(result, expected)
        self.assertEqual(weights, before)

    def test_ordinary_intervals(self):
        for r, expected in [(0, 0), (0.125, 0), (0.25, 1),
                            (0.5, 1), (0.75, 2), (0.875, 2)]:
            with self.subTest(r=r):
                self.check_pick([1, 2, 1], r, expected)





    def test_invalid_element_types(self):
        class IntSubclass(int):
            pass
        class FloatSubclass(float):
            pass
        for value in (True, False, None, '1', 1j, Fraction(1), Decimal('1'),
                      IntSubclass(1), FloatSubclass(1)):
            with self.subTest(value=repr(value)):
                weights = [10, 0, value]
                before = weights[:]
                with self.assertRaises(TypeError):
                    solution.pick(weights, 0)
                self.assertEqual(weights, before)

    def test_invalid_weight_values(self):
        for value in (-1, -0.1, -10**1000, math.inf, -math.inf, math.nan):
            with self.subTest(value=value):
                weights = [10, 0, value]
                before = weights[:]
                with self.assertRaises(ValueError):
                    solution.pick(weights, 0)
                self.assertEqual(weights, before)
        for weights in ([], (), [0], [0, 0.0, -0.0]):
            with self.subTest(weights=weights):
                with self.assertRaises(ValueError):
                    solution.pick(weights, 0.5)

    def test_invalid_r(self):
        class IntSubclass(int):
            pass
        class FloatSubclass(float):
            pass
        for r in (True, False, None, '0.5', 0j, Fraction(1, 2),
                  Decimal('0.5'), IntSubclass(0), FloatSubclass(0.5)):
            with self.subTest(r=repr(r)):
                with self.assertRaises(TypeError):
                    solution.pick([1, 2], r)
        for r in (-1, -0.001, 1, 1.01, 10**1000, math.inf, -math.inf, math.nan):
            with self.subTest(r=r):
                with self.assertRaises(ValueError):
                    solution.pick([1, 2], r)
        self.check_pick([0, 1], -0.0, 1)



if __name__ == '__main__':
    unittest.main()
