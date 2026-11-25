import unittest

import solution


class WrapTests(unittest.TestCase):

    def test_invalid_width_even_without_words(self):
        for width in (0, -1, -20):
            for text in ("", " \t", "hello"):
                with self.subTest(width=width, text=text):
                    with self.assertRaises(ValueError):
                        solution.wrap(text, width)

    def test_exact_fit_with_spaces(self):
        self.assertEqual(solution.wrap("one two six ten", 7), "one two\nsix ten")
        self.assertEqual(solution.wrap("a b c d", 5), "a b c\nd")

    def test_greedy_not_balanced(self):
        self.assertEqual(solution.wrap("aa bb c dddd ee", 6), "aa bb\nc dddd\nee")
        self.assertEqual(solution.wrap("a bb ccc", 20), "a bb ccc")

    def test_whitespace_is_normalized_not_preserved(self):
        text = " \tred\n\nblue\rgreen\v\fwhite\u00a0black\u2003 "
        self.assertEqual(solution.wrap(text, 10), "red blue\ngreen\nwhite\nblack")
        self.assertEqual(solution.wrap("a\nb", 10), "a b")







if __name__ == "__main__":
    unittest.main()
