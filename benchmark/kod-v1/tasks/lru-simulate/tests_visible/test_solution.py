import itertools
import unittest

import solution


class SinglePass:
    def __init__(self, values):
        self.values = values
        self.started = False
        self.seen = []

    def __iter__(self):
        if self.started:
            raise AssertionError('iterated twice')
        self.started = True
        for value in self.values:
            self.seen.append(value)
            yield value


class Collision:
    def __init__(self, label):
        self.label = label

    def __hash__(self):
        return 7

    def __eq__(self, other):
        return isinstance(other, Collision) and self.label == other.label


class TestSimulate(unittest.TestCase):
    def check(self, capacity, keys, expected):
        actual = solution.simulate(capacity, keys)
        self.assertIs(type(actual), list)
        self.assertEqual(actual, expected)
        self.assertTrue(all(type(item) is bool for item in actual))



    def test_zero_and_one(self):
        self.check(0, [None, None, 1, True, 'x', 'x'], [False] * 6)
        self.check(1, [1, 1, 2, 1, 1], [False, True, False, False, True])

    def test_empty_fresh_and_independent(self):
        first = solution.simulate(2, [])
        second = solution.simulate(2, ())
        self.assertEqual(first, [])
        self.assertEqual(second, [])
        self.assertIsNot(first, second)
        self.check(2, ['x'], [False])
        self.check(2, ['x'], [False])
        first.append(True)
        self.assertEqual(second, [])

    def test_iterables_and_preservation(self):
        values = ['a', 'b', 'a', 'c', 'a']
        original = values.copy()
        self.check(2, values, [False, False, True, False, True])
        self.assertEqual(values, original)
        for capacity in (0, 2):
            stream = SinglePass(values)
            expected = [False] * 5 if capacity == 0 else [False, False, True, False, True]
            self.check(capacity, stream, expected)
            self.assertEqual(stream.seen, values)
        self.check(2, (v for v in [1, 2, 1]), [False, False, True])
        self.check(10**20, 'abac', [False, False, True, False])



    def test_invalid_keys(self):
        for capacity in (0, 1, 5):
            for invalid in (None, 3, False):
                with self.subTest(capacity=capacity, invalid=invalid):
                    with self.assertRaises(TypeError):
                        solution.simulate(capacity, invalid)
            for invalid_key in ([], {}, {1}, ([],)):
                values = ['valid', invalid_key]
                with self.subTest(capacity=capacity, key=invalid_key):
                    with self.assertRaises(TypeError):
                        solution.simulate(capacity, values)
                    self.assertEqual(values[0], 'valid')
                    self.assertIs(values[1], invalid_key)



if __name__ == '__main__':
    unittest.main()
