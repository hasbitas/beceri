import unittest

import solution


class Checks(unittest.TestCase):
    def test_tail(self): self.assertEqual(solution.chunks([1, 2, 3], 2), [[1, 2], [3]])
    def test_large(self): self.assertEqual(solution.chunks([1], 5), [[1]])
    def test_no_mutation(self):
        values = [1, 2, 3]
        self.assertEqual(solution.chunks(values, 1), [[1], [2], [3]])
        self.assertEqual(values, [1, 2, 3])
