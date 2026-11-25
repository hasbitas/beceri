import unittest

import solution


class GroupAnagramsTests(unittest.TestCase):
    def test_empty_and_singleton(self):
        self.assertEqual(solution.group_anagrams([]), [])
        self.assertEqual(solution.group_anagrams(iter(())), [])
        self.assertEqual(solution.group_anagrams(["Only!"]), [["Only!"]])


    def test_repeated_letters_are_significant(self):
        self.assertEqual(
            solution.group_anagrams(["ab", "aab", "bba", "ba", "aba", "abb", "aa", "a"]),
            [["aab", "aba"], ["ab", "ba"], ["abb", "bba"], ["a"], ["aa"]],
        )

    def test_punctuation_digits_and_empty_signature(self):
        self.assertEqual(
            solution.group_anagrams(["B-a", "ab", "a b", "12", "", "!!!", "\t", "🙂"]),
            [["", "\t", "!!!", "12", "🙂"], ["a b", "ab", "B-a"]],
        )

    def test_full_text_sort_and_original_ties(self):
        self.assertEqual(
            solution.group_anagrams(["ba", "ab", "AB", "Ab", "aB", "ab", "a-b", "!BA"]),
            [["!BA", "a-b", "AB", "Ab", "aB", "ab", "ab", "ba"]],
        )

    def test_casefold_expansions(self):
        self.assertEqual(
            solution.group_anagrams(["Straße", "strasse", "STRASSE", "ß", "ss"]),
            [["STRASSE", "Straße", "strasse"], ["ss", "ß"]],
        )

    def test_nfc_equivalence_and_original_spelling(self):
        self.assertEqual(
            solution.group_anagrams(["é", "e\u0301", "É", "e"]),
            [["e\u0301", "É", "é"], ["e"]],
        )




    def test_one_pass_iterable(self):
        class OnePass:
            def __init__(self):
                self.used = False

            def __iter__(self):
                if self.used:
                    raise AssertionError("iterated more than once")
                self.used = True
                yield "cab"
                yield "abc"
                yield "x"

        self.assertEqual(solution.group_anagrams(OnePass()), [["abc", "cab"], ["x"]])



if __name__ == "__main__":
    unittest.main()
