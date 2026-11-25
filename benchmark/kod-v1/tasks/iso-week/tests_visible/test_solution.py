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



    def test_december_in_next_iso_year(self):
        for text, expected in [
            ('2014-12-29', (2015, 1)),
            ('2018-12-31', (2019, 1)),
            ('2019-12-30', (2020, 1)),
            ('2019-12-31', (2020, 1)),
        ]:
            with self.subTest(text=text):
                self.check_date(text, expected)



    def test_gregorian_cycle_boundaries(self):
        # A complete Gregorian cycle covers every weekday/leap-year arrangement.
        for year in range(2000, 2400):
            for month, days in [(1, range(1, 8)), (12, range(25, 32))]:
                for day_number in days:
                    day = datetime.date(year, month, day_number)
                    with self.subTest(date=day.isoformat()):
                        iso = day.isocalendar()
                        self.check_date(day.isoformat(), (iso[0], iso[1]))


    def test_strict_format(self):
        for text in ['', '2024-1-01', '2024-01-1', '024-01-01',
                     '02024-01-01', '10000-01-01', '20240101',
                     '2024/01/01', '+2024-01-01', '-001-01-01',
                     ' 2024-01-01', '2024-01-01 ', '2024-01-01\n',
                     '2024-01-01T00:00:00', '２０２４-０１-０１',
                     '٢٠٢٤-٠١-٠١', '2024−01−01', '2024-01-0x',
                     '2024-01-01\x00']:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.iso_week(text)

    def test_non_strings(self):
        for value in [None, True, 20240101, 1.0, b'2024-01-01',
                      [], {}, ('2024-01-01',), datetime.date(2024, 1, 1)]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.iso_week(value)


if __name__ == '__main__':
    unittest.main()
