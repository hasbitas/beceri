import itertools
import unittest

import solution


class TurkishCaseTests(unittest.TestCase):


    def test_combining_sequences_are_not_normalized(self):
        for text, upper, lower in [
            ("I\u0307", "I\u0307", "ı\u0307"),
            ("i\u0307", "İ\u0307", "i\u0307"),
            ("İ\u0307", "İ\u0307", "i\u0307"),
            ("ı\u0301I\u0323", "I\u0301I\u0323", "ı\u0301ı\u0323"),
        ]:
            with self.subTest(text=text):
                self.assertEqual(solution.tr_upper(text), upper)
                self.assertEqual(solution.tr_lower(text), lower)

    def test_unicode_expansions_are_not_resubstituted(self):
        self.assertEqual(solution.tr_upper("ß ﬃ ﬁ ı i"), "SS FFI FI I İ")
        self.assertEqual(solution.tr_lower("ẞ K İ I"), "ß k i ı")
        for text in ["éÇğşöü", "ǰΐևﬄ", "Ａｚ𐐀𐐨"]:
            with self.subTest(text=text):
                self.assertEqual(solution.tr_upper(text), text.upper())
                self.assertEqual(solution.tr_lower(text), text.lower())

    def test_context_sensitive_lowercase(self):
        for text, expected in [
            ("ΟΣ", "ος"), ("ΟΣΑ", "οσα"), ("Σ", "σ"),
            ("IΣ", "ıς"), ("İΣ", "iς"), ("ΣI", "σı"),
            ("AΣ\u0301", "aς\u0301"), ("AΣ\u0301B", "aσ\u0301b"),
            ("ΟΣ ΟΣΑ", "ος οσα"),
        ]:
            with self.subTest(text=text):
                self.assertEqual(solution.tr_lower(text), expected)

    def test_bounded_unicode_combinations(self):
        alphabet = ["i", "I", "İ", "ı", "Σ", "A", "\u0307", " ", "ﬁ"]
        for size in range(4):
            for chars in itertools.product(alphabet, repeat=size):
                text = "".join(chars)
                # Sequential replacements here cannot match each other's outputs.
                upper = text.replace("i", "İ").replace("ı", "I").upper()
                lower = text.replace("I", "ı").replace("İ", "i").lower()
                with self.subTest(text=text):
                    self.assertEqual(solution.tr_upper(text), upper)
                    self.assertEqual(solution.tr_lower(text), lower)

    def test_argument_types(self):
        for value in [None, 0, True, 1.5, b"I", bytearray(b"i"), ["i"], {"I": 1}, object()]:
            for func in [solution.tr_upper, solution.tr_lower]:
                with self.subTest(value=repr(value), func=func.__name__):
                    with self.assertRaises(TypeError):
                        func(value)



if __name__ == "__main__":
    unittest.main()
