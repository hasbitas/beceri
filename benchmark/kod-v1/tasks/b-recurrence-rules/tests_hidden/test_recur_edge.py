import copy
import datetime
import unittest

import recur
from recur.expand import expand
from recur.rule import parse_rule

D = datetime.date


def run(text, start, end):
    return expand(parse_rule(text), start, end)


class HiddenRecurTests(unittest.TestCase):
    def test_package_reexports(self):
        self.assertIs(recur.parse_rule, parse_rule)
        self.assertIs(recur.expand, expand)

    def test_parse_normalizes_lists(self):
        parsed = parse_rule("FREQ=WEEKLY;BYDAY=SU,TH,TU,SU;INTERVAL=007")
        self.assertEqual(parsed["byday"], (1, 3, 6))
        self.assertEqual(parsed["interval"], 7)
        self.assertIs(type(parsed["byday"]), tuple)
        month = parse_rule("FREQ=MONTHLY;BYMONTHDAY=15,-1,15,3;COUNT=03")
        self.assertEqual(month["bymonthday"], (-1, 3, 15))
        self.assertEqual(month["count"], 3)
        self.assertEqual(month["until"], None)
        self.assertEqual(set(month), {"freq", "interval", "byday", "bymonthday", "count", "until"})

    def test_parse_rejects_malformed_rules(self):
        bad = [
            "", "FREQ=DAILY;", ";FREQ=DAILY", "FREQ", "FREQ=", "freq=DAILY", "FREQ=daily",
            "FREQ=YEARLY", "INTERVAL=2", "FREQ=DAILY;FREQ=DAILY", "FREQ=DAILY;WKST=MO",
            "FREQ=DAILY;BYDAY=MO", "FREQ=MONTHLY;BYDAY=MO", "FREQ=WEEKLY;BYMONTHDAY=1",
            "FREQ=DAILY;COUNT=2;UNTIL=20250101", "FREQ=DAILY;INTERVAL=0",
            "FREQ=DAILY;INTERVAL=-1", "FREQ=DAILY;INTERVAL=+1", "FREQ=DAILY;COUNT=1.5",
            "FREQ=DAILY;COUNT=0", "FREQ=DAILY; COUNT=2", "FREQ=DAILY;COUNT=٣",
            "FREQ=WEEKLY;BYDAY=mo", "FREQ=WEEKLY;BYDAY=MO,", "FREQ=WEEKLY;BYDAY=MONDAY",
            "FREQ=MONTHLY;BYMONTHDAY=32", "FREQ=MONTHLY;BYMONTHDAY=0",
            "FREQ=MONTHLY;BYMONTHDAY=-2", "FREQ=MONTHLY;BYMONTHDAY=1,,2",
            "FREQ=DAILY;UNTIL=2025011", "FREQ=DAILY;UNTIL=20250230",
            "FREQ=DAILY;UNTIL=2025-01-01", "FREQ=DAILY;UNTIL=00000101",
        ]
        for text in bad:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_rule(text)
        for value in (None, 3, b"FREQ=DAILY", ["FREQ=DAILY"]):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    parse_rule(value)

    def test_weekly_interval_uses_monday_based_weeks(self):
        self.assertEqual(
            run("FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE", D(2025, 1, 1), D(2025, 1, 31)),
            [D(2025, 1, 1), D(2025, 1, 13), D(2025, 1, 15), D(2025, 1, 27), D(2025, 1, 29)],
        )
        self.assertEqual(
            run("FREQ=WEEKLY;INTERVAL=2;BYDAY=SU,MO", D(2025, 1, 5), D(2025, 2, 28)),
            [D(2025, 1, 5), D(2025, 1, 13), D(2025, 1, 19), D(2025, 1, 27),
             D(2025, 2, 2), D(2025, 2, 10), D(2025, 2, 16), D(2025, 2, 24)],
        )
        self.assertEqual(
            run("FREQ=WEEKLY;BYDAY=FR,TU;COUNT=3", D(2025, 1, 6), D(2025, 3, 1)),
            [D(2025, 1, 7), D(2025, 1, 10), D(2025, 1, 14)],
        )
        self.assertEqual(
            run("FREQ=WEEKLY;BYDAY=SU", D(2025, 1, 6), D(2025, 1, 31)),
            [D(2025, 1, 12), D(2025, 1, 19), D(2025, 1, 26)],
        )

    def test_weekly_defaults_and_pre_start_days_do_not_count(self):
        self.assertEqual(
            run("FREQ=WEEKLY", D(2025, 1, 2), D(2025, 1, 31)),
            [D(2025, 1, 2), D(2025, 1, 9), D(2025, 1, 16), D(2025, 1, 23), D(2025, 1, 30)],
        )
        self.assertEqual(
            run("FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=4", D(2025, 1, 1), D(2025, 12, 31)),
            [D(2025, 1, 1), D(2025, 1, 3), D(2025, 1, 6), D(2025, 1, 8)],
        )

    def test_monthly_last_day_and_duplicate_days(self):
        self.assertEqual(
            run("FREQ=MONTHLY;BYMONTHDAY=-1,30", D(2025, 1, 1), D(2025, 4, 30)),
            [D(2025, 1, 30), D(2025, 1, 31), D(2025, 2, 28), D(2025, 3, 30),
             D(2025, 3, 31), D(2025, 4, 30)],
        )
        self.assertEqual(
            run("FREQ=MONTHLY;BYMONTHDAY=-1", D(2024, 2, 1), D(2024, 3, 31)),
            [D(2024, 2, 29), D(2024, 3, 31)],
        )

    def test_monthly_interval_default_day_and_start_boundary(self):
        self.assertEqual(
            run("FREQ=MONTHLY;INTERVAL=5;BYMONTHDAY=15", D(2025, 1, 20), D(2026, 12, 31)),
            [D(2025, 6, 15), D(2025, 11, 15), D(2026, 4, 15), D(2026, 9, 15)],
        )
        self.assertEqual(
            run("FREQ=MONTHLY;INTERVAL=12", D(2024, 2, 29), D(2030, 1, 1)),
            [D(2024, 2, 29), D(2028, 2, 29)],
        )
        self.assertEqual(
            run("FREQ=MONTHLY;BYMONTHDAY=10,20", D(2025, 3, 10), D(2025, 4, 10)),
            [D(2025, 3, 10), D(2025, 3, 20), D(2025, 4, 10)],
        )

    def test_until_count_and_end_interplay(self):
        self.assertEqual(
            run("FREQ=DAILY;UNTIL=20250105", D(2025, 1, 3), D(2025, 1, 31)),
            [D(2025, 1, 3), D(2025, 1, 4), D(2025, 1, 5)],
        )
        self.assertEqual(
            run("FREQ=DAILY;UNTIL=20250110", D(2025, 1, 3), D(2025, 1, 4)),
            [D(2025, 1, 3), D(2025, 1, 4)],
        )
        self.assertEqual(
            run("FREQ=DAILY;COUNT=10", D(2025, 1, 3), D(2025, 1, 5)),
            [D(2025, 1, 3), D(2025, 1, 4), D(2025, 1, 5)],
        )
        self.assertEqual(run("FREQ=DAILY;UNTIL=20250101", D(2025, 1, 3), D(2025, 1, 9)), [])
        self.assertEqual(run("FREQ=DAILY", D(2025, 1, 4), D(2025, 1, 3)), [])
        self.assertEqual(run("FREQ=DAILY", D(2025, 1, 3), D(2025, 1, 3)), [D(2025, 1, 3)])

    def test_huge_intervals_and_date_limits(self):
        self.assertEqual(
            run("FREQ=WEEKLY;INTERVAL=1000000000", D(2025, 1, 1), D(2025, 12, 31)),
            [D(2025, 1, 1)],
        )
        self.assertEqual(
            run("FREQ=DAILY;INTERVAL=99999999999", D(2025, 1, 1), D(2025, 12, 31)),
            [D(2025, 1, 1)],
        )
        self.assertEqual(
            run("FREQ=MONTHLY;INTERVAL=1000000;BYMONTHDAY=1", D(2025, 1, 1), D(9999, 12, 31)),
            [D(2025, 1, 1)],
        )
        self.assertEqual(
            run("FREQ=DAILY;COUNT=5", D(9999, 12, 30), D(9999, 12, 31)),
            [D(9999, 12, 30), D(9999, 12, 31)],
        )
        self.assertEqual(
            run("FREQ=WEEKLY;BYDAY=FR,SA", D(9999, 12, 24), D(9999, 12, 31)),
            [D(9999, 12, 24), D(9999, 12, 25), D(9999, 12, 31)],
        )

    def test_expand_checks_types_and_leaves_rule_alone(self):
        rule = parse_rule("FREQ=WEEKLY;BYDAY=MO,TU;COUNT=2")
        before = copy.deepcopy(rule)
        first = expand(rule, D(2025, 1, 6), D(2025, 2, 1))
        second = expand(rule, D(2025, 1, 6), D(2025, 2, 1))
        self.assertEqual(first, [D(2025, 1, 6), D(2025, 1, 7)])
        self.assertIsNot(first, second)
        self.assertEqual(rule, before)
        stamp = datetime.datetime(2025, 1, 6)
        for start, end in ((stamp, D(2025, 2, 1)), (D(2025, 1, 6), stamp),
                           ("2025-01-06", D(2025, 2, 1)), (D(2025, 1, 6), None)):
            with self.subTest(start=start, end=end):
                with self.assertRaises(TypeError):
                    expand(rule, start, end)


if __name__ == "__main__":
    unittest.main()
