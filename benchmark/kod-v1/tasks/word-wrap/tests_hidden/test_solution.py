import unittest

import solution


class WrapTests(unittest.TestCase):
    def test_empty_and_whitespace_only(self):
        for text in ("", "  ", "\t\r\n\v\f\u2003\u00a0"):
            with self.subTest(text=text):
                self.assertEqual(solution.wrap(text, 3), "")





    def test_long_word_starts_on_fresh_line(self):
        self.assertEqual(solution.wrap("hi abcdefghijk z", 5), "hi\nabcde\nfghij\nk z")
        self.assertEqual(solution.wrap("x abcdefg hi j", 5), "x\nabcde\nfg hi\nj")

    def test_full_chunks_and_exact_width_words(self):
        self.assertEqual(solution.wrap("abcdefghij z", 5), "abcde\nfghij\nz")
        self.assertEqual(solution.wrap("abcde fghij", 5), "abcde\nfghij")
        self.assertEqual(solution.wrap("abcdefghij", 5), "abcde\nfghij")

    def test_width_one(self):
        self.assertEqual(solution.wrap("ab c\tdef", 1), "a\nb\nc\nd\ne\nf")

    def test_unicode_character_lengths_and_punctuation(self):
        self.assertEqual(solution.wrap("é🙂 猫!", 5), "é🙂 猫!")
        self.assertEqual(solution.wrap("é🙂猫!? x", 3), "é🙂猫\n!?\nx")
        self.assertEqual(solution.wrap("a\u0301 b", 4), "a\u0301 b")
        self.assertEqual(solution.wrap("one,two --end--", 7), "one,two\n--end--")

    def test_single_word_and_large_width(self):
        self.assertEqual(solution.wrap("  word  ", 4), "word")
        self.assertEqual(solution.wrap("  word  ", 100), "word")
        self.assertEqual(solution.wrap("abcdef", 4), "abcd\nef")


if __name__ == "__main__":
    unittest.main()
