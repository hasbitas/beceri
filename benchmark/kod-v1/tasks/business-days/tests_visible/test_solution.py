import unittest
import solution


class BusinessDaysTests(unittest.TestCase):
    def test_half_open_weekdays(self):
        self.assertEqual(solution.business_days('2024-01-01', '2024-01-02', []), 1)
        self.assertEqual(solution.business_days('2024-01-05', '2024-01-08', []), 1)
        self.assertEqual(solution.business_days('2024-01-06', '2024-01-08', []), 0)






    def test_calendar_limits(self):
        self.assertEqual(solution.business_days('0001-01-01', '0001-01-02', []), 1)
        self.assertEqual(solution.business_days('9999-12-30', '9999-12-31', []), 1)
        self.assertEqual(solution.business_days('9999-12-31', '9999-12-31', []), 0)

    def test_reversed_interval(self):
        with self.assertRaises(ValueError):
            solution.business_days('2024-01-08', '2024-01-01', [])

    def test_invalid_endpoint_dates(self):
        invalid = ['2024-1-01', '20240101', '2024-01-01\n', ' 2024-01-01',
                   '2023-02-29', '1900-02-29', '2024-04-31', '0000-01-01',
                   '10000-01-01', '2024-00-01', '2024-01-00',
                   '２０２４-０１-０１', '2024-01-01T00:00:00', None, 20240101]
        for value in invalid:
            with self.subTest(value=value, position='start'):
                with self.assertRaises(ValueError):
                    solution.business_days(value, '2024-03-01', [])
            with self.subTest(value=value, position='end'):
                with self.assertRaises(ValueError):
                    solution.business_days('2024-01-01', value, [])

    def test_all_holidays_are_validated(self):
        for bad in ['2023-02-29', '2020-1-01', None, 123, '２０２４-０１-０１']:
            for end in ['2024-01-01', '2024-01-08']:
                with self.subTest(bad=bad, end=end):
                    with self.assertRaises(ValueError):
                        solution.business_days('2024-01-01', end, iter(['2024-01-02', bad]))




if __name__ == '__main__':
    unittest.main()
