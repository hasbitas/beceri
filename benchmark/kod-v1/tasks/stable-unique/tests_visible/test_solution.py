import unittest

import solution


class Checks(unittest.TestCase):
    def test_order(self): self.assertEqual(solution.unique([3, 1, 3, 2]), [3, 1, 2])
    def test_mixed(self): self.assertEqual(solution.unique([1, "a", 1]), [1, "a"])
