import unittest

import solution


class Checks(unittest.TestCase):
    def test_empty(self): self.assertEqual(solution.unique([]), [])
    def test_strings(self): self.assertEqual(solution.unique(["z", "a", "z"]), ["z", "a"])
    def test_no_mutation(self):
        values = [3, 1, 3]
        output = solution.unique(values)
        self.assertEqual(values, [3, 1, 3])
        self.assertIsNot(output, values)
