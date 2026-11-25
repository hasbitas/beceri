import datetime
import fractions
import unittest

import billing
from billing.months import add_months, last_day, whole_months_between
from billing.periods import billing_periods, next_due, period_of, prorate

D = datetime.date


class HiddenBillingTests(unittest.TestCase):
    def test_package_reexports(self):
        for name, func in (("add_months", add_months), ("last_day", last_day),
                           ("whole_months_between", whole_months_between),
                           ("billing_periods", billing_periods), ("period_of", period_of),
                           ("next_due", next_due), ("prorate", prorate)):
            self.assertIs(getattr(billing, name), func)

    def test_last_day(self):
        self.assertEqual(last_day(2024, 2), D(2024, 2, 29))
        self.assertEqual(last_day(2025, 2), D(2025, 2, 28))
        self.assertEqual(last_day(1900, 2), D(1900, 2, 28))
        self.assertEqual(last_day(2000, 2), D(2000, 2, 29))
        self.assertEqual(last_day(2025, 12), D(2025, 12, 31))
        self.assertEqual(last_day(9999, 12), D(9999, 12, 31))
        self.assertEqual(last_day(1, 1), D(1, 1, 31))
        for year, month in ((0, 1), (10000, 1), (2025, 0), (2025, 13), (-5, 3)):
            with self.subTest(year=year, month=month):
                with self.assertRaises(ValueError):
                    last_day(year, month)
        for year, month in ((True, 1), (2025, True), ("2025", 1), (2025, 1.0)):
            with self.subTest(year=year, month=month):
                with self.assertRaises(TypeError):
                    last_day(year, month)

    def test_add_months_clamping_and_direction(self):
        cases = [
            (D(2025, 1, 31), 13, D(2026, 2, 28)),
            (D(2024, 1, 31), 13, D(2025, 2, 28)),
            (D(2025, 1, 31), 0, D(2025, 1, 31)),
            (D(2025, 1, 15), -1, D(2024, 12, 15)),
            (D(2025, 1, 15), -12, D(2024, 1, 15)),
            (D(2025, 1, 31), -2, D(2024, 11, 30)),
            (D(2025, 5, 31), -3, D(2025, 2, 28)),
            (D(2024, 2, 29), 12, D(2025, 2, 28)),
            (D(2024, 2, 29), 48, D(2028, 2, 29)),
            (D(2025, 12, 31), 2, D(2026, 2, 28)),
            (D(2025, 6, 30), 6, D(2025, 12, 30)),
            (D(2025, 6, 15), 12000, D(3025, 6, 15)),
            (D(9999, 11, 30), 1, D(9999, 12, 30)),
        ]
        for day, n, expected in cases:
            with self.subTest(day=day, n=n):
                result = add_months(day, n)
                self.assertEqual(result, expected)
                self.assertIs(type(result), D)

    def test_add_months_errors(self):
        for day, n in ((D(9999, 12, 1), 1), (D(1, 1, 1), -1), (D(2025, 1, 1), 10 ** 6),
                       (D(2025, 1, 1), -10 ** 6)):
            with self.subTest(day=day, n=n):
                with self.assertRaises(ValueError):
                    add_months(day, n)
        for day, n in ((datetime.datetime(2025, 1, 1), 1), ("2025-01-01", 1), (D(2025, 1, 1), 1.0),
                       (D(2025, 1, 1), False), (D(2025, 1, 1), None)):
            with self.subTest(day=day, n=n):
                with self.assertRaises(TypeError):
                    add_months(day, n)

    def test_whole_months_between_uses_clamped_dates(self):
        cases = [
            (D(2025, 1, 31), D(2025, 2, 27), 0),
            (D(2025, 1, 31), D(2025, 3, 30), 1),
            (D(2025, 1, 31), D(2025, 3, 31), 2),
            (D(2025, 1, 31), D(2025, 4, 30), 3),
            (D(2025, 8, 30), D(2026, 2, 28), 6),
            (D(2024, 2, 29), D(2025, 2, 28), 12),
            (D(2024, 2, 29), D(2025, 2, 27), 11),
            (D(2025, 5, 20), D(2025, 5, 20), 0),
            (D(2025, 5, 20), D(2025, 5, 31), 0),
            (D(2024, 12, 31), D(2025, 1, 30), 0),
            (D(2024, 12, 31), D(2025, 1, 31), 1),
            (D(2020, 3, 1), D(2025, 3, 1), 60),
        ]
        for start, end, expected in cases:
            with self.subTest(start=start, end=end):
                self.assertEqual(whole_months_between(start, end), expected)
        with self.assertRaises(ValueError):
            whole_months_between(D(2025, 3, 2), D(2025, 3, 1))
        with self.assertRaises(TypeError):
            whole_months_between(D(2025, 3, 1), datetime.datetime(2025, 4, 1))

    def test_billing_periods_do_not_drift(self):
        self.assertEqual(
            billing_periods(D(2025, 1, 31), 4),
            [(D(2025, 1, 31), D(2025, 2, 28)), (D(2025, 2, 28), D(2025, 3, 31)),
             (D(2025, 3, 31), D(2025, 4, 30)), (D(2025, 4, 30), D(2025, 5, 31))],
        )
        self.assertEqual(
            billing_periods(D(2024, 2, 29), 3, 3),
            [(D(2024, 2, 29), D(2024, 5, 29)), (D(2024, 5, 29), D(2024, 8, 29)),
             (D(2024, 8, 29), D(2024, 11, 29))],
        )
        yearly = billing_periods(D(2028, 2, 29), 5, 12)
        self.assertEqual(yearly[3], (D(2031, 2, 28), D(2032, 2, 29)))
        self.assertEqual(yearly[4], (D(2032, 2, 29), D(2033, 2, 28)))
        first = billing_periods(D(2025, 1, 1), 2)
        self.assertIsInstance(first, list)
        self.assertIsNot(first, billing_periods(D(2025, 1, 1), 2))

    def test_billing_periods_errors(self):
        self.assertEqual(billing_periods(D(9999, 6, 15), 0, 12), [])
        for args in ((D(9999, 6, 15), 1, 12), (D(2025, 1, 1), -1), (D(2025, 1, 1), 1, 0),
                     (D(2025, 1, 1), 1, -2), (D(2025, 1, 1), 100000)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    billing_periods(*args)
        for args in (("2025-01-01", 1), (D(2025, 1, 1), 1.5), (D(2025, 1, 1), True),
                     (D(2025, 1, 1), 1, True), (D(2025, 1, 1), 1, "1"),
                     (D(2025, 1, 1), -1, "x")):
            with self.subTest(args=args):
                with self.assertRaises(TypeError):
                    billing_periods(*args)

    def test_period_of_around_clamped_boundaries(self):
        anchor = D(2025, 1, 31)
        cases = [
            (1, D(2025, 1, 31), (0, (D(2025, 1, 31), D(2025, 2, 28)))),
            (1, D(2025, 2, 27), (0, (D(2025, 1, 31), D(2025, 2, 28)))),
            (1, D(2025, 2, 28), (1, (D(2025, 2, 28), D(2025, 3, 31)))),
            (1, D(2025, 3, 30), (1, (D(2025, 2, 28), D(2025, 3, 31)))),
            (1, D(2025, 3, 31), (2, (D(2025, 3, 31), D(2025, 4, 30)))),
            (3, D(2025, 4, 29), (0, (D(2025, 1, 31), D(2025, 4, 30)))),
            (3, D(2025, 4, 30), (1, (D(2025, 4, 30), D(2025, 7, 31)))),
            (3, D(2025, 7, 30), (1, (D(2025, 4, 30), D(2025, 7, 31)))),
            (3, D(2025, 7, 31), (2, (D(2025, 7, 31), D(2025, 10, 31)))),
        ]
        for step, day, expected in cases:
            with self.subTest(step=step, day=day):
                self.assertEqual(period_of(anchor, step, day), expected)
        with self.assertRaises(ValueError):
            period_of(anchor, 1, D(2025, 1, 30))
        with self.assertRaises(ValueError):
            period_of(anchor, 0, D(2025, 2, 1))
        with self.assertRaises(ValueError):
            period_of(D(2025, 1, 1), 12, D(9999, 12, 31))

    def test_period_of_agrees_with_billing_periods(self):
        for anchor in (D(2024, 1, 31), D(2024, 2, 29), D(2023, 12, 30), D(2025, 5, 15)):
            for step in (1, 2, 5, 12):
                periods = billing_periods(anchor, 400, step)
                day = anchor
                for _ in range(1200):
                    index, (start, end) = period_of(anchor, step, day)
                    self.assertEqual(periods[index], (start, end))
                    self.assertTrue(start <= day < end, (anchor, step, day))
                    day += datetime.timedelta(days=1)

    def test_next_due(self):
        anchor = D(2025, 1, 31)
        self.assertEqual(next_due(anchor, 1, D(2024, 6, 1)), anchor)
        self.assertEqual(next_due(anchor, 1, D(2025, 1, 30)), anchor)
        self.assertEqual(next_due(anchor, 1, anchor), D(2025, 2, 28))
        self.assertEqual(next_due(anchor, 1, D(2025, 2, 28)), D(2025, 3, 31))
        self.assertEqual(next_due(anchor, 1, D(2025, 3, 30)), D(2025, 3, 31))
        self.assertEqual(next_due(anchor, 1, D(2025, 3, 31)), D(2025, 4, 30))
        self.assertEqual(next_due(anchor, 6, D(2025, 7, 30)), D(2025, 7, 31))
        with self.assertRaises(ValueError):
            next_due(anchor, 0, D(2025, 2, 1))
        with self.assertRaises(TypeError):
            next_due(anchor, 1, datetime.datetime(2025, 2, 1))

    def test_prorate(self):
        value = prorate(D(2025, 1, 1), 1, D(2025, 1, 16))
        self.assertEqual(value, fractions.Fraction(16, 31))
        self.assertIsInstance(value, fractions.Fraction)
        self.assertEqual(prorate(D(2025, 1, 1), 1, D(2025, 1, 1)), 1)
        self.assertEqual(prorate(D(2025, 1, 1), 1, D(2025, 1, 31)), fractions.Fraction(1, 31))
        self.assertEqual(prorate(D(2025, 1, 31), 1, D(2025, 2, 28)), 1)
        self.assertEqual(prorate(D(2025, 1, 31), 1, D(2025, 3, 15)), fractions.Fraction(16, 31))
        self.assertEqual(prorate(D(2024, 1, 31), 3, D(2024, 4, 30)), 1)
        self.assertEqual(prorate(D(2024, 1, 31), 3, D(2024, 6, 15)), fractions.Fraction(46, 92))
        with self.assertRaises(ValueError):
            prorate(D(2025, 2, 1), 1, D(2025, 1, 31))


if __name__ == "__main__":
    unittest.main()
