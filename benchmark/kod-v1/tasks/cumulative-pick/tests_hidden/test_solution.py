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


    def test_zero_weights_and_boundaries(self):
        for r, expected in [(0, 1), (0.25, 1), (0.5, 4),
                            (math.nextafter(0.5, 0), 1),
                            (math.nextafter(0.5, 1), 4),
                            (math.nextafter(1.0, 0), 4)]:
            with self.subTest(r=r):
                self.check_pick([0, 2, 0, -0.0, 2, 0], r, expected)
        self.check_pick((0, 0, 7, 0), 0, 2)
        self.check_pick((0, 0, 7, 0), 0.999, 2)

    def test_exact_extreme_values(self):
        tiny = float.fromhex('0x0.0000000000001p-1022')
        huge = float.fromhex('0x1.fffffffffffffp+1023')
        for weights in ([tiny, tiny], [huge, huge], [10**1000, 10**1000]):
            with self.subTest(weights_type=type(weights[0])):
                self.check_pick(weights, 0.5, 1)
                self.check_pick(weights, math.nextafter(0.5, 0), 0)
        self.check_pick([2**54, 1, 2**54], 0.5, 1)
        self.check_pick([huge, tiny], math.nextafter(1.0, 0), 0)
        self.check_pick([tiny, huge], 0, 0)
        self.check_pick([tiny, huge], tiny, 1)
        # The binary value of 0.1 is larger than the exact fraction 1/10.
        self.check_pick([0.1, 0.9], 0.1, 1)

    def test_container_subclasses(self):
        class Weights(list):
            pass
        class TupleWeights(tuple):
            pass
        self.check_pick(Weights([0, 1, 3]), 0.5, 2)
        self.check_pick(TupleWeights((0, 1, 3)), 0, 1)

    def test_invalid_container_types(self):
        for weights in (None, 1, '123', {0: 1}, {1, 2}, iter([1, 2]),
                        (x for x in [1, 2])):
            with self.subTest(container=type(weights)):
                with self.assertRaises(TypeError):
                    solution.pick(weights, 0)




    def test_bounded_integer_unit_cell_oracle(self):
        # Expand integer weights to unit cells, independently of a prefix scan.
        for weights in itertools.product(range(3), repeat=4):
            cells = [i for i, w in enumerate(weights) for _ in range(w)]
            if not cells:
                continue
            for numerator in range(16):
                r = numerator / 16
                expected = cells[(numerator * len(cells)) // 16]
                with self.subTest(weights=weights, r=r):
                    self.check_pick(weights, r, expected)


if __name__ == '__main__':
    unittest.main()
