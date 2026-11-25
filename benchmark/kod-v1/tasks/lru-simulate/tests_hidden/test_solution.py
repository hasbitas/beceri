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

    def test_hit_refreshes_recency(self):
        self.check(2, ['a', 'b', 'a', 'c', 'a', 'b'],
                   [False, False, True, False, True, False])

    def test_eviction_and_reinsertion(self):
        self.check(3, 'abcadbeca',
                   [False, False, False, True, False, False, False, False, False])




    def test_equality_and_hash_collisions(self):
        self.check(2, [1, True, 1.0, '1', None, True],
                   [False, True, True, False, False, False])
        a, b, c = Collision('a'), Collision('b'), Collision('c')
        self.check(2, [a, b, Collision('a'), c, a, b],
                   [False, False, True, False, True, False])
        self.check(3, [None, '', (), None, '', ()],
                   [False, False, False, True, True, True])

    def test_invalid_capacity_before_consumption(self):
        class IntegerSubclass(int):
            pass
        for capacity in (True, False, 2.0, '2', None, IntegerSubclass(2)):
            stream = SinglePass([1])
            with self.subTest(capacity=capacity):
                with self.assertRaises(TypeError):
                    solution.simulate(capacity, stream)
                self.assertFalse(stream.started)
        stream = SinglePass([1])
        with self.assertRaises(ValueError):
            solution.simulate(-1, stream)
        self.assertFalse(stream.started)


    def test_bounded_sequences_against_last_request_model(self):
        # Independent model: residents are the capacity most recently
        # requested distinct keys, recomputed from the entire prior history.
        for size in range(7):
            for keys in itertools.product('abc', repeat=size):
                for capacity in range(5):
                    expected = []
                    for index, key in enumerate(keys):
                        recent = []
                        for prior in reversed(keys[:index]):
                            if prior not in recent:
                                recent.append(prior)
                        expected.append(key in recent[:capacity])
                    with self.subTest(keys=keys, capacity=capacity):
                        self.check(capacity, keys, expected)


if __name__ == '__main__':
    unittest.main()
