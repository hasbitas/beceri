import unittest

import solution


class Checks(unittest.TestCase):
    def test_below(self): self.assertEqual(solution.clamp(-2, 0, 5), 0)
    def test_above(self): self.assertEqual(solution.clamp(9, 0, 5), 5)
    def test_reversed(self):
        with self.assertRaises(ValueError): solution.clamp(3, 5, 0)
