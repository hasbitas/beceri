import unittest

import solution


class MovingAverageTests(unittest.TestCase):
    def assertAverages(self, actual, expected):
        self.assertIs(type(actual), list)
        self.assertEqual(len(actual), len(expected))
        for got, want in zip(actual, expected):
            self.assertIs(type(got), float)
            self.assertAlmostEqual(got, want, places=12)

    def test_complete_windows_and_default(self):
        self.assertAverages(solution.moving_average([2, 4, 9, -1, 7], 3),
                            [5.0, 4.0, 5.0])
        self.assertAverages(solution.moving_average([2, 4, 9], 3, False), [5.0])

    def test_partial_prefix_and_sliding(self):
        self.assertAverages(solution.moving_average([6, 2, 7, -3, 8], 3, True),
                            [6.0, 4.0, 5.0, 2.0, 4.0])






    def test_partial_validation(self):
        for bad in (0, 1, None, '', [], 'yes'):
            with self.subTest(partial=bad), self.assertRaises(TypeError):
                solution.moving_average([], 2, bad)



    def test_non_iterable(self):
        for bad in (None, 42, 3.5):
            with self.subTest(values=bad), self.assertRaises(TypeError):
                solution.moving_average(bad, 2)


if __name__ == '__main__':
    unittest.main()
