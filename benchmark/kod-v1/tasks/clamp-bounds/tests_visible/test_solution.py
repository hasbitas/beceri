import unittest

import solution


class Checks(unittest.TestCase):
    def test_inside(self): self.assertEqual(solution.clamp(3, 0, 5), 3)
    def test_equal_bounds(self): self.assertEqual(solution.clamp(-5, 2, 2), 2)
