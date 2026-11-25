import copy
from fractions import Fraction
import itertools
import unittest

import solution


class IntChild(int):
    pass


class ListChild(list):
    pass


def fan_area(points):
    # Independent triangulation about the first vertex.
    ox, oy = map(Fraction, points[0])
    total = Fraction(0)
    for a, b in zip(points[1:], points[2:]):
        ax, ay = Fraction(a[0]) - ox, Fraction(a[1]) - oy
        bx, by = Fraction(b[0]) - ox, Fraction(b[1]) - oy
        total += ax * by - ay * bx
    return total / 2


class AreaTests(unittest.TestCase):
    def check_area(self, points, expected):
        before = copy.deepcopy(points)
        result = solution.area(points)
        self.assertIs(type(result), float)
        self.assertEqual(result, float(expected))
        self.assertEqual(points, before)




    def test_exact_float_and_boundary_coordinates(self):
        cases = [
            [(0, 0), (1, 0), (0, 2.0 ** -100)],
            [(1e9, 1e9), (1e9 - 1, 1e9), (1e9, 1e9 - 1)],
            [(-1e9, -1e9), (1e9, -1e9), (1e9, 1e9), (-1e9, 1e9)],
            [(0.1, 0.2), (0.3, 0.2), (0.1, 0.7)],
        ]
        for points in cases:
            with self.subTest(points=points):
                self.check_area(points, fan_area(points))
                self.check_area(points[::-1], -fan_area(points))

    def test_too_few_repeated_and_collinear(self):
        cases = [[], [(0, 0)], [(0, 0), (1, 1)],
                 [(0, 0), (1, 1), (0, 0)],
                 [(0, 0), (1, 1), (2, 2)],
                 [(0, 0), (2, 0), (0, 2), (2, 0)],
                 [(0, 0), (2, 0), (0, 2), (0, 0), (0, 0)],
                 [(0, 0), (2, 0), (2.0, -0.0), (0, 2)]]
        for points in cases:
            with self.subTest(points=points):
                before = copy.deepcopy(points)
                with self.assertRaises(ValueError):
                    solution.area(points)
                self.assertEqual(points, before)



    def test_coordinate_range(self):
        for value in [float('nan'), float('inf'), -float('inf'),
                      1000000001, -1000000001, 10 ** 400]:
            for point in [(value, 1), (1, value)]:
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        solution.area([(0, 0), (2, 0), point])


    def test_bounded_vertex_orders_against_triangulation(self):
        vertices = [(-2, -1), (2, -1), (3, 2), (0, 1), (-1, 3)]
        for count in (3, 4, 5):
            for ring in itertools.permutations(vertices, count):
                exact = fan_area(ring)
                with self.subTest(ring=ring):
                    if exact == 0:
                        with self.assertRaises(ValueError):
                            solution.area(ring)
                    else:
                        self.check_area(ring, exact)


if __name__ == '__main__':
    unittest.main()
