import copy
import unittest

import solution


class LocateTests(unittest.TestCase):
    def check(self, polygon, cases):
        for point, expected in cases:
            with self.subTest(polygon=polygon, point=point):
                self.assertEqual(solution.locate(point, polygon), expected)




    def test_ray_through_vertices(self):
        self.check([(0, 3), (3, 0), (6, 3), (3, 6)], [
            ((-1, 3), 'outside'), ((1, 3), 'inside'),
            ((3, 3), 'inside'), ((5, 3), 'inside'),
            ((7, 3), 'outside'), ((-1, 6), 'outside'),
            ((4, 6), 'outside'), ((3, 6), 'boundary')])

    def test_orientation_start_and_closure(self):
        polygon = [(0, 0), (8, 0), (8, 6), (4, 3), (0, 6)]
        cases = [((4, 1), 'inside'), ((4, 5), 'outside'),
                 ((4, 3), 'boundary'), ((2, 4), 'inside'),
                 ((-1, 3), 'outside'), ((7, 4), 'inside')]
        for reverse in (False, True):
            vertices = polygon[::-1] if reverse else polygon
            for offset in range(len(vertices)):
                rotated = vertices[offset:] + vertices[:offset]
                self.check(rotated, cases)
                self.check(tuple(rotated + [rotated[0]]), cases)

    def test_collinear_and_duplicate_vertices(self):
        polygon = [(0, 0), (0, 0), (3, 0), (6, 0), (6, 4),
                   (6, 4), (3, 4), (0, 4), (0, 0), (0, 0)]
        self.check(polygon, [((3, 2), 'inside'), ((3, 0), 'boundary'),
                             ((4, 4), 'boundary'), ((0, 0), 'boundary'),
                             ((7, 0), 'outside'), ((-1, 0), 'outside')])

    def test_small_grid_rectangles_independent_oracle(self):
        for left, bottom, right, top in [(-3, -2, 4, 3), (0, 0, 1, 1)]:
            polygon = [(left, bottom), (right, bottom),
                       (right, top), (left, top)]
            for x in range(-4, 6):
                for y in range(-3, 5):
                    if not (left <= x <= right and bottom <= y <= top):
                        expected = 'outside'
                    elif x in (left, right) or y in (bottom, top):
                        expected = 'boundary'
                    else:
                        expected = 'inside'
                    self.check(polygon, [((x, y), expected)])

    def test_large_translation_narrow_rectangle(self):
        for shift in (10**20, -10**20, 10**100):
            polygon = [(shift, -3), (shift + 4, -3),
                       (shift + 4, 5), (shift, 5)]
            self.check(polygon, [((shift + 1, 0), 'inside'),
                                 ((shift + 3, 0), 'inside'),
                                 ((shift + 4, 0), 'boundary'),
                                 ((shift - 1, 0), 'outside'),
                                 ((shift + 5, 0), 'outside')])


    def test_inputs_are_not_mutated(self):
        for point, expected in [([2, 2], 'inside'), ([5, 2], 'outside'),
                                ([4, 2], 'boundary')]:
            polygon = [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]]
            before = copy.deepcopy((point, polygon))
            self.assertEqual(solution.locate(point, polygon), expected)
            self.assertEqual((point, polygon), before)
            self.assertEqual(solution.locate(tuple(point), tuple(map(tuple, polygon))),
                             expected)


if __name__ == '__main__':
    unittest.main()
