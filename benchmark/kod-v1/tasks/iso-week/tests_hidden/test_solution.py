import datetime
import unittest

import solution


class IsoWeekTests(unittest.TestCase):
    def check_date(self, text, expected):
        result = solution.iso_week(text)
        self.assertIs(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(type(item) is int for item in result))
        self.assertEqual(result, expected)

    def test_ordinary_dates(self):
        for text, expected in [
            ('2024-01-15', (2024, 3)),
            ('2024-06-12', (2024, 24)),
            ('2023-07-01', (2023, 26)),
            ('2000-02-29', (2000, 9)),
        ]:
            with self.subTest(text=text):
                self.check_date(text, expected)

    def test_january_in_previous_iso_year(self):
        for text, expected in [
            ('2016-01-01', (2015, 53)),
            ('2016-01-03', (2015, 53)),
            ('2021-01-01', (2020, 53)),
            ('2022-01-02', (2021, 52)),
            ('2023-01-01', (2022, 52)),
        ]:
            with self.subTest(text=text):
                self.check_date(text, expected)


    def test_week_transitions(self):
        for text, expected in [
            ('2015-12-27', (2015, 52)),
            ('2015-12-28', (2015, 53)),
            ('2016-01-04', (2016, 1)),
            ('2024-01-07', (2024, 1)),
            ('2024-01-08', (2024, 2)),
        ]:
            with self.subTest(text=text):
                self.check_date(text, expected)

    def test_full_range_and_leap_centuries(self):
        for text in ['0001-01-01', '0001-12-31', '0004-02-29',
                     '0099-12-31', '0100-03-01', '0400-02-29',
                     '1600-02-29', '1900-03-01', '2400-02-29',
                     '9999-01-01', '9999-12-31']:
            with self.subTest(text=text):
                day = datetime.date.fromisoformat(text)
                iso = day.isocalendar()
                self.check_date(text, (iso[0], iso[1]))


    def test_invalid_calendar_dates(self):
        for text in ['0000-01-01', '2024-00-01', '2024-13-01',
                     '2024-01-00', '2024-01-32', '2024-04-31',
                     '2023-02-29', '1900-02-29', '2100-02-29',
                     '2024-02-30', '9999-12-32']:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.iso_week(text)




if __name__ == '__main__':
    unittest.main()
