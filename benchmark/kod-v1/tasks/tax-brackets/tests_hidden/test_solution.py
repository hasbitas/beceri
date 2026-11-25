import copy
import itertools
import unittest
from fractions import Fraction

import solution


class IntSubclass(int):
    pass


class TaxTests(unittest.TestCase):
    def check_tax(self, income, brackets, expected):
        before = copy.deepcopy(brackets)
        result = solution.tax(income, brackets)
        self.assertIs(type(result), int)
        self.assertEqual(result, expected)
        self.assertEqual(brackets, before)

    def test_progressive_examples(self):
        schedule = [(10000, 1000), (30000, 2000), (None, 3500)]
        for income, expected in [(0, 0), (5000, 500), (10000, 1000),
                                 (20000, 3000), (30000, 5000),
                                 (40000, 8500)]:
            with self.subTest(income=income):
                self.check_tax(income, schedule, expected)


    def test_single_bracket_half_up(self):
        for rate, expected in [(0, 0), (4999, 0), (5000, 1),
                               (5001, 1), (10000, 1)]:
            with self.subTest(rate=rate):
                self.check_tax(1, ((None, rate),), expected)
        self.check_tax(5, [[None, 5000]], 3)
        self.check_tax(1, [(None, 150)], 0)
        self.check_tax(100, [(None, 150)], 2)



    def test_bounded_independent_unit_oracle(self):
        # Assign each individual kurus to its bracket, then use exact fractions.
        for rates in itertools.product((0, 2499, 5000, 7501, 10000), repeat=3):
            schedule = [(2, rates[0]), (5, rates[1]), (None, rates[2])]
            for income in range(9):
                pieces = [Fraction(0), Fraction(0), Fraction(0)]
                for unit in range(1, income + 1):
                    index = 0 if unit <= 2 else 1 if unit <= 5 else 2
                    pieces[index] += Fraction(rates[index], 10000)
                expected = sum(int(piece + Fraction(1, 2)) for piece in pieces)
                with self.subTest(rates=rates, income=income):
                    self.assertEqual(solution.tax(income, schedule), expected)

    def test_invalid_income(self):
        for value in (True, False, 1.0, '1', None, [], IntSubclass(1)):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.tax(value, [(None, 1000)])
        with self.assertRaises(ValueError):
            solution.tax(-1, [(None, 1000)])

    def test_invalid_container_and_entry_types(self):
        for schedule in (None, 'schedule', {}, {1, 2}, iter([(None, 0)])):
            with self.subTest(schedule=type(schedule)):
                with self.assertRaises(TypeError):
                    solution.tax(0, schedule)
        for entry in (None, 'ab', {None: 0}, 7):
            with self.subTest(entry=entry):
                with self.assertRaises(TypeError):
                    solution.tax(0, [entry])
        for schedule in ([], (), [()], [(None,)], [(None, 1, 2)]):
            with self.subTest(schedule=schedule):
                with self.assertRaises(ValueError):
                    solution.tax(0, schedule)

    def test_invalid_limits(self):
        for limit in (True, 1.0, '2', IntSubclass(2)):
            with self.subTest(limit=limit):
                with self.assertRaises(TypeError):
                    solution.tax(0, [(limit, 0), (None, 0)])
        schedules = [
            [(0, 0), (None, 0)], [(-1, 0), (None, 0)],
            [(2, 0), (2, 0), (None, 0)],
            [(3, 0), (2, 0), (None, 0)],
            [(None, 0), (None, 0)], [(5, 0)],
            [('unlimited', 0)], [(False, 0)],
        ]
        for schedule in schedules:
            with self.subTest(schedule=schedule):
                before = copy.deepcopy(schedule)
                with self.assertRaises(ValueError):
                    solution.tax(0, schedule)
                self.assertEqual(schedule, before)


    def test_invalid_unused_late_limit(self):
        schedule = [[100, 1000], [90, 2000], [None, 0]]
        before = copy.deepcopy(schedule)
        with self.assertRaises(ValueError):
            solution.tax(1, schedule)
        self.assertEqual(schedule, before)


if __name__ == '__main__':
    unittest.main()
