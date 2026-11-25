import itertools
import unittest

import solution


class Integer(int):
    pass


class ListSubclass(list):
    pass


class TupleSubclass(tuple):
    pass


class WindowMaxTests(unittest.TestCase):





    def test_accepted_subclasses(self):
        for values in (ListSubclass([Integer(4), 1, 3]),
                       TupleSubclass((Integer(4), 1, 3))):
            self.assertEqual(solution.window_max(values, Integer(2)), [4, 3])

    def test_invalid_outer_types(self):
        for values in (None, 5, True, '123', b'123', {1, 2}, {0: 1}, range(3)):
            with self.subTest(values=values):
                with self.assertRaises(TypeError):
                    solution.window_max(values, 1)

    def test_invalid_k_types(self):
        for k in (True, False, 1.0, '2', None, [], complex(2)):
            with self.subTest(k=k):
                with self.assertRaises(TypeError):
                    solution.window_max([1, 2], k)

    def test_nonpositive_k(self):
        for values in ([], (), [1, 2]):
            for k in (0, -1, -10 ** 100):
                with self.subTest(values=values, k=k):
                    with self.assertRaises(ValueError):
                        solution.window_max(values, k)


    def test_validation_precedence(self):
        with self.assertRaises(TypeError):
            solution.window_max(None, 0)
        with self.assertRaises(TypeError):
            solution.window_max([None], False)
        with self.assertRaises(ValueError):
            solution.window_max([None], 0)
        with self.assertRaises(ValueError):
            solution.window_max([None], -3)


    def test_exhaustive_small_inputs(self):
        for length in range(6):
            for values in itertools.product((-2, 0, 3), repeat=length):
                for k in range(1, length + 3):
                    expected = [max(values[start:start + k])
                                for start in range(length - k + 1)]
                    with self.subTest(values=values, k=k):
                        self.assertEqual(solution.window_max(values, k), expected)



if __name__ == '__main__':
    unittest.main()
