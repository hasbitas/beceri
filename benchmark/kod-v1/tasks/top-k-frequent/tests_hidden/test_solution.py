import itertools
import unittest

import solution


class TopKTests(unittest.TestCase):
    def test_frequency_is_primary(self):
        data = ["z", "a", "z", "b", "b", "z", "a", "x"]
        self.assertEqual(solution.top_k(data, 3), ["z", "a", "b"])


    def test_casefold_not_lowercase(self):
        data = ["t", "ß", "st", "ss", "SS", "Straße", "STRASSE"]
        expected = ["SS", "ss", "ß", "st", "STRASSE", "Straße", "t"]
        self.assertEqual(solution.top_k(data, 100), expected)
        self.assertEqual(solution.top_k(reversed(data), 3), expected[:3])

    def test_other_unicode_ties(self):
        self.assertEqual(solution.top_k(["σ", "ς", "Σ"], 3), ["Σ", "ς", "σ"])
        self.assertEqual(solution.top_k(["é", "e\u0301", "", "É"], 9),
                         ["", "e\u0301", "É", "é"])

    def test_exact_counts_not_folded_counts(self):
        data = ["ß", "ss", "SS", "z", "z", "SS", "z"]
        self.assertEqual(solution.top_k(data, 9), ["z", "SS", "ss", "ß"])


    def test_string_as_iterable(self):
        self.assertEqual(solution.top_k("bAaabB", 8), ["a", "b", "A", "B"])


    def test_invalid_k_and_validation_precedence(self):
        class Unusable:
            def __iter__(self):
                raise AssertionError("items accessed before k validation")

        for k in [True, False, 1.0, "1", None, [], complex(1, 0)]:
            with self.subTest(k=k), self.assertRaises(TypeError):
                solution.top_k(Unusable(), k)
        for k in [-1, -100]:
            with self.subTest(k=k), self.assertRaises(ValueError):
                solution.top_k(Unusable(), k)


    def test_subclasses_and_ownership(self):
        class Text(str):
            pass

        class Number(int):
            pass

        data = [Text("b"), "a", "b"]
        before = list(data)
        first = solution.top_k(data, Number(2))
        second = solution.top_k(data, 2)
        self.assertIs(type(first), list)
        self.assertEqual(first, ["b", "a"])
        self.assertEqual(data, before)
        self.assertIsNot(first, second)
        self.assertIsNot(first, data)
        first.clear()
        self.assertEqual(second, ["b", "a"])
        self.assertIsNot(solution.top_k([], 0), solution.top_k([], 0))
        invalid = ["b", "a", 4]
        with self.assertRaises(TypeError):
            solution.top_k(invalid, 1)
        self.assertEqual(invalid, ["b", "a", 4])



if __name__ == "__main__":
    unittest.main()
