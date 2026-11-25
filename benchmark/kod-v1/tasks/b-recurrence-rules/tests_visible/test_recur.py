import datetime
import unittest

from recur.expand import expand
from recur.rule import parse_rule

D = datetime.date


class VisibleRecurTests(unittest.TestCase):
    def test_parse_fills_defaults_and_orders_weekdays(self):
        self.assertEqual(
            parse_rule("FREQ=WEEKLY;BYDAY=FR,MO"),
            {
                "freq": "WEEKLY",
                "interval": 1,
                "byday": (0, 4),
                "bymonthday": (),
                "count": None,
                "until": None,
            },
        )
        self.assertEqual(parse_rule("FREQ=DAILY;UNTIL=20250131")["until"], D(2025, 1, 31))

    def test_daily_with_interval_and_count(self):
        rule = parse_rule("FREQ=DAILY;INTERVAL=3;COUNT=4")
        self.assertEqual(
            expand(rule, D(2025, 1, 1), D(2025, 12, 31)),
            [D(2025, 1, 1), D(2025, 1, 4), D(2025, 1, 7), D(2025, 1, 10)],
        )

    def test_weekly_two_weekdays(self):
        rule = parse_rule("FREQ=WEEKLY;BYDAY=MO,FR;COUNT=3")
        self.assertEqual(
            expand(rule, D(2025, 1, 6), D(2025, 3, 1)),
            [D(2025, 1, 6), D(2025, 1, 10), D(2025, 1, 13)],
        )

    def test_monthly_skips_months_without_the_day(self):
        rule = parse_rule("FREQ=MONTHLY;BYMONTHDAY=31")
        self.assertEqual(
            expand(rule, D(2025, 1, 31), D(2025, 6, 30)),
            [D(2025, 1, 31), D(2025, 3, 31), D(2025, 5, 31)],
        )

    def test_basic_errors(self):
        with self.assertRaises(ValueError):
            parse_rule("FREQ=YEARLY")
        with self.assertRaises(ValueError):
            parse_rule("FREQ=DAILY;COUNT=2;UNTIL=20250101")
        with self.assertRaises(TypeError):
            parse_rule(None)
        with self.assertRaises(TypeError):
            expand(parse_rule("FREQ=DAILY"), datetime.datetime(2025, 1, 1), D(2025, 1, 2))


if __name__ == "__main__":
    unittest.main()
