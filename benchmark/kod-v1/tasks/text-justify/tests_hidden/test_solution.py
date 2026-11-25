import itertools
import unittest

import solution


class JustifyTests(unittest.TestCase):
    def check_case(self, words, width, expected):
        original = words[:]
        actual = solution.justify(words, width)
        self.assertIsInstance(actual, list)
        self.assertEqual(actual, expected)
        self.assertEqual(words, original)
        for line in actual:
            self.assertEqual(len(line), width)

    def test_empty(self):
        self.check_case([], 1, [])
        self.check_case([], 20, [])

    def test_single_word(self):
        self.check_case(['hello'], 8, ['hello   '])
        self.check_case(['hello'], 5, ['hello'])



    def test_leftmost_remainder(self):
        self.check_case(['a', 'b', 'c', 'dddddd'], 8,
                        ['a   b  c', 'dddddd  '])
        self.check_case(['a', 'b', 'c', 'd', 'xxxxxxxx'], 10,
                        ['a  b  c  d', 'xxxxxxxx  '])
        self.check_case(['a', 'b', 'c', 'd', 'xxxxxxxx'], 9,
                        ['a  b  c d', 'xxxxxxxx '])

    def test_greedy_exact_fit(self):
        self.check_case(['ab', 'cd', 'ef', 'gh'], 5,
                        ['ab cd', 'ef gh'])
        self.check_case(['a', 'b', 'cc'], 4, ['a  b', 'cc  '])


    def test_unicode_codepoint_lengths(self):
        self.check_case(['猫', 'é', '🙂', 'abcde'], 6,
                        ['猫  é 🙂', 'abcde '])
        self.check_case(['e\u0301', '猫', 'xx'], 4,
                        ['e\u0301 猫', 'xx  '])

    def test_repeated_calls_and_duplicates(self):
        words = ['x', 'x', 'x', 'xxxxx']
        self.check_case(words, 6, ['x  x x', 'xxxxx '])
        self.check_case(['other'], 5, ['other'])
        self.check_case(words, 6, ['x  x x', 'xxxxx '])



if __name__ == '__main__':
    unittest.main()
