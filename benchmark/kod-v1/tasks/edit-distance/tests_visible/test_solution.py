import itertools
import unittest

import solution


def reference(a, b):
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        rows[i][0] = i
    for j in range(len(b) + 1):
        rows[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            rows[i][j] = min(rows[i - 1][j] + 1,
                             rows[i][j - 1] + 1,
                             rows[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return rows[-1][-1]


class DistanceTests(unittest.TestCase):
    def check_distance(self, a, b, expected):
        for left, right in ((a, b), (b, a)):
            self.assertEqual(solution.distance(left, right), expected)
            self.assertEqual(solution.distance(left, right, None), expected)
            for limit in sorted({0, 1, max(0, expected - 1), expected, expected + 1, 20}):
                with self.subTest(a=left, b=right, limit=limit):
                    result = solution.distance(left, right, limit=limit)
                    self.assertIsInstance(result, int)
                    self.assertEqual(result, min(expected, limit + 1))

    def test_standard_edits(self):
        for a, b, d in [('kitten', 'sitting', 3), ('flaw', 'lawn', 2),
                        ('abc', 'axc', 1), ('abc', 'abxc', 1),
                        ('Saturday', 'Sunday', 3), ('ab', 'ba', 2)]:
            self.check_distance(a, b, d)


    def test_inclusive_limit(self):
        for a, b in [('a', 'b'), ('xabcd', 'yabcd'),
                     ('abcdef', 'abcxyz'), ('aaaa', 'bbbb'),
                     ('prefix-tail', 'prefix-sail')]:
            d = reference(a, b)
            self.assertEqual(solution.distance(a, b, d), d)
            self.assertEqual(solution.distance(a, b, d - 1), d)


    def test_unicode_and_literal_comparison(self):
        for a, b, d in [('é', 'e\u0301', 2), ('😀', '', 1),
                        ('😀a', '😀b', 1), ('A', 'a', 1),
                        (' x\n', 'x', 2), ('a\x00b', 'ab', 1),
                        ('你好', '您好', 1)]:
            self.check_distance(a, b, d)

    def test_small_exhaustive(self):
        words = [''.join(chars) for n in range(4)
                 for chars in itertools.product('ab', repeat=n)]
        for a in words:
            for b in words:
                d = reference(a, b)
                self.assertEqual(solution.distance(a, b), d)
                for limit in range(5):
                    with self.subTest(a=a, b=b, limit=limit):
                        self.assertEqual(solution.distance(a, b, limit), min(d, limit + 1))






if __name__ == '__main__':
    unittest.main()
