import unittest

import solution


class Checks(unittest.TestCase):
    def test_empty(self): self.assertEqual(solution.chunks([], 2), [])
    def test_invalid(self):
        for size in (0, -1):
            with self.assertRaises(ValueError): solution.chunks([1], size)
