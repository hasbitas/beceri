import unittest
import solution


class BusinessDaysTests(unittest.TestCase):

    def test_equal_endpoints(self):
        self.assertEqual(solution.business_days('2024-01-01', '2024-01-01', []), 0)
        self.assertEqual(solution.business_days('2024-01-06', '2024-01-06', []), 0)

    def test_holiday_boundaries_and_weekends(self):
        holidays = ['2024-01-01', '2024-01-06', '2024-01-07',
                    '2024-01-08', '2023-12-29', '2024-01-09']
        self.assertEqual(solution.business_days('2024-01-01', '2024-01-08', holidays), 4)

    def test_duplicate_holidays_and_no_mutation(self):
        holidays = ['2024-01-03', '2024-01-03', '2024-01-06']
        original = holidays.copy()
        self.assertEqual(solution.business_days('2024-01-01', '2024-01-07', holidays), 4)
        self.assertEqual(holidays, original)

    def test_one_shot_iterator(self):
        holidays = (value for value in ['2024-02-29', '2024-02-29', '2024-03-02'])
        self.assertEqual(solution.business_days('2024-02-28', '2024-03-04', holidays), 2)
        self.assertEqual(list(holidays), [])

    def test_leap_and_year_boundaries(self):
        self.assertEqual(solution.business_days('2024-02-28', '2024-03-02', []), 3)
        self.assertEqual(solution.business_days('2023-12-29', '2024-01-03', []), 3)
        self.assertEqual(solution.business_days('2024-01-01', '2025-01-01', []), 262)





    def test_non_iterable_holidays(self):
        for holidays in [None, 42]:
            with self.subTest(holidays=holidays):
                with self.assertRaises(TypeError):
                    solution.business_days('2024-01-01', '2024-01-08', holidays)

    def test_century_leap_date_and_return_type(self):
        result = solution.business_days('2000-02-28', '2000-03-04', ('2000-02-29',))
        self.assertIs(type(result), int)
        self.assertEqual(result, 4)


if __name__ == '__main__':
    unittest.main()
