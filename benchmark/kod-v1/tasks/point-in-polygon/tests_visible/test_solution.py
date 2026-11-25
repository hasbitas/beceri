import copy
import unittest

import solution


class LocateTests(unittest.TestCase):
    def check(self, polygon, cases):
        for point, expected in cases:
            with self.subTest(polygon=polygon, point=point):
                self.assertEqual(solution.locate(point, polygon), expected)

    def test_square_and_extensions(self):
        self.check([(0, 0), (8, 0), (8, 8), (0, 8)], [
            ((4, 4), 'inside'), ((-1, 4), 'outside'),
            ((9, 4), 'outside'), ((4, -1), 'outside'),
            ((4, 9), 'outside'), ((0, 0), 'boundary'),
            ((8, 8), 'boundary'), ((4, 0), 'boundary'),
            ((8, 4), 'boundary'), ((0, 4), 'boundary'),
            ((4, 8), 'boundary'), ((-1, 0), 'outside'),
            ((9, 8), 'outside'), ((0, 10), 'outside')])

    def test_diagonal_edges(self):
        self.check([(0, 0), (12, 0), (0, 12)], [
            ((1, 1), 'inside'), ((5, 6), 'inside'),
            ((5, 7), 'boundary'), ((5, 8), 'outside'),
            ((-1, 13), 'outside'), ((13, -1), 'outside'),
            ((0, 12), 'boundary'), ((12, 0), 'boundary')])

    def test_concave_notch(self):
        polygon = [(0, 0), (8, 0), (8, 8), (6, 8),
                   (6, 2), (2, 2), (2, 8), (0, 8)]
        self.check(polygon, [((1, 7), 'inside'), ((7, 7), 'inside'),
                             ((4, 1), 'inside'), ((4, 5), 'outside'),
                             ((4, 2), 'boundary'), ((2, 6), 'boundary'),
                             ((6, 2), 'boundary'), ((4, 8), 'outside')])






    def test_near_sloping_edge_exact_integer_geometry(self):
        n = 10**80
        # At height 1 the sloping edge has x = n + 1/2.
        polygon = [(0, 0), (n + 1, 0), (n, 2), (0, 2)]
        self.check(polygon, [((n, 1), 'inside'), ((n + 1, 1), 'outside'),
                             ((n, 2), 'boundary'), ((n - 1, 2), 'boundary')])
        huge = 10**400
        self.check([(0, 0), (huge, 0), (0, huge)], [
            ((1, 1), 'inside'), ((huge // 2, huge // 2), 'boundary'),
            ((huge, 1), 'outside')])



if __name__ == '__main__':
    unittest.main()
