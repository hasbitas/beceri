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

    def test_basic_and_order(self):
        scores = [100, 0, 90, 80, 70, 60, 59, 89, 79, 69, 60]
        self.assertEqual(solution.letters(scores, self.cuts),
                         list("AFABCD FBCD D".replace(" ", "")))
        self.assertEqual(solution.letters((0, 100, -0.0), self.cuts), ["F", "A", "F"])

    def test_even_and_odd_halfway_boundaries(self):
        cuts = {"A": 91, "B": 81, "C": 71, "D": 61}
        self.assertEqual(solution.letters([90.5, 80.5, 70.5, 60.5], cuts), list("ABCD"))
        self.assertEqual(solution.letters([89.5, 79.5, 69.5, 59.5], self.cuts), list("ABCD"))

    def test_binary_neighbors_and_no_epsilon(self):
        for minimum in range(1, 101):
            cuts = {"A": minimum, "B": minimum - 1, "C": minimum - 2, "D": minimum - 3}
            if minimum < 3:
                cuts = {"A": 3, "B": 2, "C": 1, "D": 0}
            boundary = minimum - 0.5
            scores = [math.nextafter(boundary, -math.inf), boundary,
                      math.nextafter(boundary, math.inf)]
            below = next((g for g in "ABCD" if minimum - 1 >= cuts[g]), "F")
            at = next((g for g in "ABCD" if minimum >= cuts[g]), "F")
            with self.subTest(minimum=minimum):
                self.assertEqual(solution.letters(scores, cuts), [below, at, at])



    def test_empty_fresh_outputs_and_preservation(self):
        scores = [95, 10, 85]
        cuts = {"D": 60, "B": 80, "A": 90, "C": 70}
        saved = list(cuts.items())
        result = solution.letters(scores, cuts)
        self.assertIs(type(result), list)
        self.assertIsNot(result, scores)
        result.append("X")
        self.assertEqual(scores, [95, 10, 85])
        self.assertEqual(list(cuts.items()), saved)
        empty = []
        first = solution.letters(empty, cuts)
        second = solution.letters((), cuts)
        self.assertEqual(first, [])
        self.assertEqual(second, [])
        self.assertIsNot(first, empty)
        self.assertIsNot(first, second)



    def test_threshold_ranges_and_order(self):
        cases = [(-1, 80, 70, 60), (101, 80, 70, 60), (90, 80, 70, -1),
                 (90, 90, 70, 60), (90, 80, 80, 60), (90, 80, 70, 70),
                 (60, 70, 80, 90), (90, 95, 70, 60), (90, 80, 50, 60)]
        for values in cases:
            cuts = dict(zip("ABCD", values))
            saved = cuts.copy()
            with self.subTest(values=values), self.assertRaises(ValueError):
                solution.letters([], cuts)
            self.assertEqual(cuts, saved)

    def test_score_containers(self):
        for scores in (None, "90", 90, {90}, {"score": 90}, iter([90]),
                       ListChild([90]), TupleChild((90,))):
            with self.subTest(kind=type(scores)), self.assertRaises(TypeError):
                solution.letters(scores, self.cuts)

    def test_score_types_and_values(self):
        for bad in (True, False, "90", None, [], IntChild(90), FloatChild(90),
                    Decimal("90"), Fraction(90)):
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                solution.letters([100, bad], self.cuts)
        for bad in (-1, 101, -0.001, 100.001, float("inf"), -float("inf"),
                    float("nan"), 10 ** 400, -(10 ** 400)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                solution.letters([100, bad], self.cuts)



if __name__ == "__main__":
    unittest.main()
