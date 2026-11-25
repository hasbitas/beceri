import unittest
from itertools import combinations_with_replacement

import solution


class AllowedTests(unittest.TestCase):
    def check(self, timestamps, limit, window, expected):
        before = timestamps[:]
        result = solution.allowed(timestamps, limit, window)
        self.assertIsInstance(result, list)
        self.assertEqual(result, expected)
        self.assertTrue(all(type(item) is bool for item in result))
        self.assertEqual(timestamps, before)

    def test_empty_and_zero_limit(self):
        self.check([], 3, 5, [])
        self.check([], 0, 1, [])
        self.check([0, 0, 1, 50], 0, 2, [False] * 4)

    def test_exact_expiration(self):
        self.check([0, 4, 5, 9, 10], 1, 5,
                   [True, False, True, False, True])
        self.check([0, 1, 5, 6], 2, 5, [True] * 4)


    def test_rejections_do_not_extend_history(self):
        self.check([0, 1, 2, 3, 4, 5, 6, 10], 1, 5,
                   [True, False, False, False, False, True, False, True])


    def test_large_exact_integers(self):
        base = 10 ** 100
        self.check([base, base + 1, base + 6, base + 7], 1, 7,
                   [True, False, False, True])
        self.check([0, base - 1, base], 1, base, [True, False, True])



    def test_invalid_timestamp_containers(self):
        for stamps in [None, (), (0, 1), '01', 5, {0, 1}, {0: 1}]:
            with self.subTest(stamps=stamps):
                with self.assertRaises(ValueError):
                    solution.allowed(stamps, 0, 1)

    def test_invalid_entries_validate_even_when_no_capacity(self):
        for stamps in [[-1], [0, -1], [2, 1], [True], [False],
                       [0, 1.0], [None], ['0'], [[]], [0, 3, 2]]:
            before = stamps[:]
            for limit in [0, 2]:
                with self.subTest(stamps=stamps, limit=limit):
                    with self.assertRaises(ValueError):
                        solution.allowed(stamps, limit, 3)
                    self.assertEqual(stamps, before)

    def test_exhaustive_small_sequences(self):
        for length in range(6):
            for seq in combinations_with_replacement(range(5), length):
                for limit in range(4):
                    for window in range(1, 5):
                        accepted = []
                        expected = []
                        for t in seq:
                            count = sum(t - window < s <= t for s in accepted)
                            ok = count < limit
                            expected.append(ok)
                            if ok:
                                accepted.append(t)
                        with self.subTest(seq=seq, limit=limit, window=window):
                            self.check(list(seq), limit, window, expected)


if __name__ == '__main__':
    unittest.main()
