import datetime
import unittest

from billing.months import add_months, whole_months_between
from billing.periods import billing_periods, next_due, period_of

D = datetime.date


class VisibleBillingTests(unittest.TestCase):
    def test_add_months_clamps_to_month_end(self):
        self.assertEqual(add_months(D(2025, 1, 31), 1), D(2025, 2, 28))
        self.assertEqual(add_months(D(2025, 3, 15), 1), D(2025, 4, 15))
        self.assertEqual(add_months(D(2025, 3, 31), -1), D(2025, 2, 28))
        self.assertEqual(add_months(D(2024, 1, 31), 1), D(2024, 2, 29))

    def test_whole_months_between(self):
        self.assertEqual(whole_months_between(D(2025, 1, 15), D(2025, 3, 14)), 1)
        self.assertEqual(whole_months_between(D(2025, 1, 15), D(2025, 3, 15)), 2)
        self.assertEqual(whole_months_between(D(2025, 1, 31), D(2025, 2, 28)), 1)

    def test_billing_periods_simple(self):
        self.assertEqual(
            billing_periods(D(2025, 3, 15), 2),
            [(D(2025, 3, 15), D(2025, 4, 15)), (D(2025, 4, 15), D(2025, 5, 15))],
        )
        self.assertEqual(billing_periods(D(2025, 3, 15), 0, 3), [])

    def test_period_of_and_next_due(self):
        self.assertEqual(
            period_of(D(2025, 1, 15), 1, D(2025, 2, 10)),
            (0, (D(2025, 1, 15), D(2025, 2, 15))),
        )
        self.assertEqual(next_due(D(2025, 1, 15), 1, D(2025, 1, 1)), D(2025, 1, 15))
        self.assertEqual(next_due(D(2025, 1, 15), 1, D(2025, 2, 10)), D(2025, 2, 15))

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            add_months(datetime.datetime(2025, 1, 1), 1)
        with self.assertRaises(TypeError):
            add_months(D(2025, 1, 1), True)
        with self.assertRaises(ValueError):
            billing_periods(D(2025, 1, 1), 2, 0)


if __name__ == "__main__":
    unittest.main()
