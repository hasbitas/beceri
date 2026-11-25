import itertools
import math
import unittest
from decimal import Decimal
from fractions import Fraction

import solution


class IntChild(int):
    pass


class FloatChild(float):
    pass


class ListChild(list):
    pass


class TupleChild(tuple):
    pass


class DictChild(dict):
    pass


class LettersTests(unittest.TestCase):
    def setUp(self):
        self.cuts = {"A": 90, "B": 80, "C": 70, "D": 60}




    def test_dense_quarter_scores_independent_oracle(self):
        scores = [n / 4 for n in range(401)]
        for cuts in ({"A": 99, "B": 76, "C": 34, "D": 1},
                     {"A": 100, "B": 99, "C": 1, "D": 0}, self.cuts):
            # Qualifying for integer cut c is equivalent to score >= c - 1/2.
            expected = [next((g for g in "ABCD" if Fraction(s) >= Fraction(2 * cuts[g] - 1, 2)), "F")
                        for s in scores]
            self.assertEqual(solution.letters(scores, cuts), expected)

    def test_dictionary_order(self):
        for order in itertools.permutations("ABCD"):
            cuts = {g: self.cuts[g] for g in order}
            self.assertEqual(solution.letters([95, 85, 75, 65, 55], cuts), list("ABCDF"))


    def test_threshold_container_and_keys(self):
        for cuts in (None, [], (), DictChild(self.cuts), 90):
            with self.subTest(cuts=cuts), self.assertRaises(TypeError):
                solution.letters([], cuts)
        for cuts in ({}, {"A": 90, "B": 80, "C": 70},
                     dict(self.cuts, F=0), {"a": 90, "B": 80, "C": 70, "D": 60},
                     {1: 90, "B": 80, "C": 70, "D": 60}):
            with self.subTest(cuts=cuts), self.assertRaises(ValueError):
                solution.letters([], cuts)

    def test_threshold_value_types(self):
        for grade in "ABCD":
            for bad in (True, False, 60.0, "60", None, IntChild(60), Decimal(60), Fraction(60)):
                cuts = dict(self.cuts)
                cuts[grade] = bad
                with self.subTest(grade=grade, bad=bad), self.assertRaises(TypeError):
                    solution.letters([], cuts)




    def test_validation_precedence_and_failure_preservation(self):
        with self.assertRaises(ValueError):
            solution.letters(None, {})
        with self.assertRaises(ValueError):
            solution.letters([True], dict(self.cuts, A=101))
        with self.assertRaises(ValueError):
            solution.letters(None, dict(self.cuts, extra=None))
        with self.assertRaises(TypeError):
            solution.letters(None, {"A": 101, "B": 80, "C": 70, "D": False})
        with self.assertRaises(TypeError):
            solution.letters([True, -1], self.cuts)
        with self.assertRaises(ValueError):
            solution.letters([-1, True], self.cuts)
        scores = [95, 85, -1]
        before = scores.copy()
        cuts_before = list(self.cuts.items())
        with self.assertRaises(ValueError):
            solution.letters(scores, self.cuts)
        self.assertEqual(scores, before)
        self.assertEqual(list(self.cuts.items()), cuts_before)


if __name__ == "__main__":
    unittest.main()
