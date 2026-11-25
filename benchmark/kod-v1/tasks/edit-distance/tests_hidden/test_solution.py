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


    def test_empty_and_equal(self):
        for text in ['', 'a', 'hello', '\x00\n', '😀']:
            self.check_distance(text, text, 0)
            self.check_distance('', text, len(text))


    def test_exact_sentinel_not_actual_distance(self):
        for limit in [0, 1, 2, 3]:
            self.assertEqual(solution.distance('abcdefgh', 'XXXXXXXX', limit), limit + 1)
            self.assertEqual(solution.distance('', 'abcdefgh', limit), limit + 1)



    def test_invalid_string_arguments(self):
        for value in [None, 0, True, b'abc', ['a'], ('a',), {}]:
            for a, b in [(value, ''), ('', value), (value, value)]:
                with self.subTest(a=a, b=b):
                    with self.assertRaises(TypeError):
                        solution.distance(a, b)

    def test_invalid_limits_even_for_trivial_inputs(self):
        for a, b in [('', ''), ('same', 'same'), ('', 'x'), ('a', 'b')]:
            for value in [True, False, 1.0, -1.0, '1', [], {}]:
                with self.subTest(a=a, b=b, limit=value):
                    with self.assertRaises(TypeError):
                        solution.distance(a, b, value)
            for value in [-1, -100]:
                with self.assertRaises(ValueError):
                    solution.distance(a, b, value)

    def test_subclasses(self):
        class Text(str):
            pass

        class Count(int):
            pass

        self.assertEqual(solution.distance(Text('abc'), Text('axc')), 1)
        self.assertEqual(solution.distance(Text('abc'), 'axc', Count(1)), 1)
        with self.assertRaises(ValueError):
            solution.distance('', '', Count(-1))

    def test_long_strings_and_repeated_calls(self):
        a = 'a' * 1500
        b = 'a' * 1499 + 'b'
        self.assertEqual(solution.distance(a, b), 1)
        self.assertEqual(solution.distance(a, b, 1), 1)
        self.assertEqual(solution.distance(a, b, 0), 1)
        self.assertEqual(solution.distance(a, a, 0), 0)
        self.assertEqual(solution.distance('cat', 'cut'), 1)
        self.assertEqual(solution.distance('cat', 'cut', 0), 1)
        self.assertEqual(solution.distance('cat', 'cut', 2), 1)
        self.assertEqual(solution.distance('cat', 'cut'), 1)


if __name__ == '__main__':
    unittest.main()
