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




    def test_singleton_and_endpoints(self):
        for p in [0, 0.001, 25, 50, 99.999, 100]:
            self.check_result((-3,), p, -3)
        self.check_result([4, -8, 2], 0, -8)
        self.check_result([4, -8, 2], 100, 4)

    def test_container_variants_and_order(self):
        for ordering in itertools.permutations([-5, 1, 9]):
            for factory in [list, tuple, ListSubclass, TupleSubclass]:
                with self.subTest(ordering=ordering, factory=factory):
                    self.check_result(factory(ordering), 25, -2)

    def test_outer_type(self):
        for values in [None, 7, '123', {1, 2}, {1: 2}, iter([1, 2]), range(3)]:
            with self.subTest(values=type(values)):
                with self.assertRaises(TypeError):
                    solution.percentile(values, 50)

    def test_invalid_number_types(self):
        bad = [True, False, None, '5', 2j, Decimal('2'), Fraction(1, 2),
               IntSubclass(2), FloatSubclass(2)]
        for item in bad:
            with self.subTest(item=repr(item)):
                with self.assertRaises(TypeError):
                    solution.percentile([1, 2], item)
                for p in [0, 50, 100]:
                    with self.assertRaises(TypeError):
                        solution.percentile([1, item], p)
                with self.assertRaises(TypeError):
                    solution.percentile([item], 50)


    def test_empty_and_validation_precedence(self):
        for values in [[], ()]:
            with self.assertRaises(ValueError):
                solution.percentile(values, 50)
            with self.assertRaises(TypeError):
                solution.percentile(values, '50')
        with self.assertRaises(TypeError):
            solution.percentile(None, float('nan'))
        with self.assertRaises(ValueError):
            solution.percentile([None], -1)
        with self.assertRaises(ValueError):
            solution.percentile([float('nan'), None], 50)
        with self.assertRaises(TypeError):
            solution.percentile([None, float('nan')], 50)





if __name__ == '__main__':
    unittest.main()
