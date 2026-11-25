import unittest

import solution


class GroupAnagramsTests(unittest.TestCase):

    def test_sizes_and_signature_tiebreak(self):
        words = ["tea", "dog", "bat", "eat", "god", "tab", "ate", "z"]
        self.assertEqual(
            solution.group_anagrams(words),
            [["ate", "eat", "tea"], ["bat", "tab"], ["dog", "god"], ["z"]],
        )






    def test_casefold_before_normalization(self):
        # U+01F0 folds to j plus combining caron, which NFC composes again.
        self.assertEqual(
            solution.group_anagrams(["ǰ", "j", "j\u030c", "J\u030c"]),
            [["J\u030c", "j\u030c", "ǰ"], ["j"]],
        )

    def test_unicode_letters_and_nonletters(self):
        self.assertEqual(
            solution.group_anagrams(["京东", "东京", "İ", "i", "I", "²", "\u0301"]),
            [["I", "i", "İ"], ["²", "\u0301"], ["东京", "京东"]],
        )

    def test_empty_signature_wins_equal_size_tie(self):
        self.assertEqual(
            solution.group_anagrams(["b", "a", "?", "B", "A", ""]),
            [["", "?"], ["A", "a"], ["B", "b"]],
        )


    def test_no_mutation_and_fresh_lists(self):
        words = ["tea", "eat", "tea", "x"]
        before = words[:]
        first = solution.group_anagrams(words)
        second = solution.group_anagrams(words)
        self.assertEqual(words, before)
        self.assertEqual(first, [["eat", "tea", "tea"], ["x"]])
        self.assertEqual(second, first)
        self.assertIsNot(first, second)
        for left, right in zip(first, second):
            self.assertIsNot(left, right)
            self.assertIsNot(left, words)
        first[0].append("changed")
        first.append(["new"])
        self.assertEqual(second, [["eat", "tea", "tea"], ["x"]])
        self.assertEqual(words, before)


if __name__ == "__main__":
    unittest.main()
