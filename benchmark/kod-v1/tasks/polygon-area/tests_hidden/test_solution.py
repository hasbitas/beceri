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

    def test_known_shapes_and_orientation(self):
        for points, expected in [
            ([(1, 1), (5, 1), (1, 4)], 6),
            ([(2, 3), (7, 3), (7, 5), (2, 5)], 10),
            ([(0, 0), (4, 0), (4, 1), (1, 1), (1, 4), (0, 4)], 7),
        ]:
            with self.subTest(points=points):
                self.check_area(points, expected)
                self.check_area(points[::-1], -expected)
                for k in range(len(points)):
                    self.check_area(points[k:] + points[:k], expected)

    def test_closed_and_mixed_containers(self):
        points = [[0, 0], (3, 0), [0, 2]]
        self.check_area(points, 3)
        self.check_area(tuple(points) + ((0.0, -0.0),), 3)
        self.check_area(points[::-1] + [points[-1]], -3)

    def test_self_intersections(self):
        points = [(0, 0), (4, 3), (0, 3), (2, 0)]
        self.check_area(points, 3)
        self.check_area(points[::-1], -3)
        with self.assertRaises(ValueError):
            solution.area([(0, 0), (2, 2), (0, 2), (2, 0)])



    def test_container_types(self):
        for value in [None, 'abc', 5, {}, iter([(0, 0), (1, 0), (0, 1)]),
                      ListChild([(0, 0), (1, 0), (0, 1)])]:
            with self.subTest(value=type(value)):
                with self.assertRaises(TypeError):
                    solution.area(value)
        for point in [None, '12', {0: 0, 1: 0}, ListChild([0, 1])]:
            with self.subTest(point=point):
                with self.assertRaises(TypeError):
                    solution.area([(0, 0), (1, 0), point])

    def test_point_lengths_and_coordinate_types(self):
        for point in [[], [1], [1, 2, 3]]:
            with self.assertRaises(ValueError):
                solution.area([(0, 0), (2, 0), point])
        for value in [True, False, '1', None, 1j, Fraction(1, 2), IntChild(1)]:
            for point in [(value, 1), (1, value)]:
                with self.subTest(point=point):
                    with self.assertRaises(TypeError):
                        solution.area([(0, 0), (2, 0), point])


    def test_failure_preserves_nested_lists(self):
        points = [[0, 0], [3, 0], [0, 2], [4, 'bad']]
        before = copy.deepcopy(points)
        identities = [id(point) for point in points]
        with self.assertRaises(TypeError):
            solution.area(points)
        self.assertEqual(points, before)
        self.assertEqual([id(point) for point in points], identities)



if __name__ == '__main__':
    unittest.main()
