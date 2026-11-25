import unittest

import solution


class MovingAverageTests(unittest.TestCase):
    def assertAverages(self, actual, expected):
        self.assertIs(type(actual), list)
        self.assertEqual(len(actual), len(expected))
        for got, want in zip(actual, expected):
            self.assertIs(type(got), float)
            self.assertAlmostEqual(got, want, places=12)



    def test_window_larger_than_input(self):
        self.assertAverages(solution.moving_average([4, -2, 10], 10), [])
        self.assertAverages(solution.moving_average([4, -2, 10], 10, True),
                            [4.0, 1.0, 4.0])

    def test_empty_and_unit_window(self):
        for partial in (False, True):
            self.assertAverages(solution.moving_average([], 3, partial), [])
            self.assertAverages(solution.moving_average(iter(()), 1, partial), [])
            self.assertAverages(solution.moving_average([3, -2.5, 0], 1, partial),
                                [3.0, -2.5, 0.0])

    def test_one_pass_and_no_mutation(self):
        values = [1, 2, 5, 8]
        self.assertAverages(solution.moving_average(values, 2), [1.5, 3.5, 6.5])
        self.assertEqual(values, [1, 2, 5, 8])
        iterator = (x for x in values)
        self.assertAverages(solution.moving_average(iterator, 2, True),
                            [1.0, 1.5, 3.5, 6.5])
        self.assertEqual(list(iterator), [])
        self.assertAverages(solution.moving_average((2, 8, 5), 2), [5.0, 6.5])

    def test_fractional_results_are_not_rounded(self):
        self.assertAverages(solution.moving_average([0.25, -1.0, 2.0, 0.5], 3),
                            [1.25 / 3, 1.5 / 3])
        self.assertAverages(solution.moving_average([-2, -3, -6], 2, True),
                            [-2.0, -2.5, -4.5])

    def test_window_validation(self):
        for bad in (True, False, 2.0, '2', None):
            with self.subTest(window=bad), self.assertRaises(TypeError):
                solution.moving_average([], bad)
        for bad in (0, -1, -100):
            with self.subTest(window=bad), self.assertRaises(ValueError):
                solution.moving_average([], bad)


    def test_validation_order_before_consumption(self):
        def forbidden():
            raise AssertionError('input consumed before argument validation')
            yield 1
        with self.assertRaises(TypeError):
            solution.moving_average(forbidden(), 1.0, None)
        with self.assertRaises(ValueError):
            solution.moving_average(forbidden(), 0, None)
        with self.assertRaises(TypeError):
            solution.moving_average(forbidden(), 1, None)

    def test_invalid_elements_even_without_complete_window(self):
        for bad in (True, False, '3', None, 1 + 0j, [], object()):
            for partial in (False, True):
                with self.subTest(value=repr(bad), partial=partial):
                    with self.assertRaises(TypeError):
                        solution.moving_average(iter([1, bad]), 9, partial)
        for bad in (float('nan'), float('inf'), float('-inf')):
            for partial in (False, True):
                with self.subTest(value=bad, partial=partial):
                    with self.assertRaises(ValueError):
                        solution.moving_average([1, bad], 9, partial)
        with self.assertRaises(TypeError):
            solution.moving_average([1, 2, 'bad'], 2)



if __name__ == '__main__':
    unittest.main()
