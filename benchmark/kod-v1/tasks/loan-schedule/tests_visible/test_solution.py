import unittest
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext

import solution

D = Decimal


class ScheduleTests(unittest.TestCase):
    def assert_rows(self, actual, values):
        expected = [dict(zip(('month', 'payment', 'interest', 'principal', 'balance'),
                             (i, *(D(v) for v in row))))
                    for i, row in enumerate(values, 1)]
        self.assertEqual(actual, expected)
        for i, row in enumerate(actual, 1):
            self.assertIs(type(row['month']), int)
            self.assertEqual(row['month'], i)
            for key in ('payment', 'interest', 'principal', 'balance'):
                self.assertIsInstance(row[key], D)
                self.assertEqual(row[key].as_tuple().exponent, -2)




    def test_early_payoff_keeps_rows_and_half_up_payment(self):
        self.assert_rows(solution.schedule('0.05', 0, 10), [
            ('0.01', '0.00', '0.01', '0.04'),
            ('0.01', '0.00', '0.01', '0.03'),
            ('0.01', '0.00', '0.01', '0.02'),
            ('0.01', '0.00', '0.01', '0.01'),
            ('0.01', '0.00', '0.01', '0.00'),
        ] + [('0.00', '0.00', '0.00', '0.00')] * 5)



    def test_one_month(self):
        self.assert_rows(solution.schedule('123.45', 12, 1), [
            ('124.68', '1.23', '123.45', '0.00')])


    def test_invalid_inputs(self):
        invalid_principals = (True, False, None, [], {}, complex(1), '', 'bad',
                              'NaN', 'sNaN', 'Infinity', '-Infinity', float('nan'),
                              float('inf'), 0, -1, '0.001', '1.001', '1000000000000.01')
        invalid_rates = (True, None, [], complex(1), '', 'bad', 'NaN', 'sNaN',
                         'Infinity', float('nan'), -1, '0.0000001', '100.000001')
        invalid_months = (True, False, 0, -1, 601, 2.0, D('2'), '2', None)
        for principal in invalid_principals:
            with self.subTest(principal=principal), self.assertRaises(ValueError):
                solution.schedule(principal, 12, 3)
        for rate in invalid_rates:
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                solution.schedule(100, rate, 3)
        for months in invalid_months:
            with self.subTest(months=months), self.assertRaises(ValueError):
                solution.schedule(100, 12, months)


    def test_boundaries_and_accounting(self):
        cases = [('1000000000000', '100', 600), ('0.01', '0.000001', 600),
                 ('50000.99', '5.75', 360), ('999.99', '0', 7),
                 ('1000000000000', '0.000001', 600)]
        with localcontext() as ctx:
            ctx.prec = 50
            ctx.rounding = ROUND_HALF_UP
            for principal, rate, months in cases:
                with self.subTest(principal=principal, rate=rate, months=months):
                    rows = solution.schedule(principal, rate, months)
                    self.assertIsInstance(rows, list)
                    self.assertEqual(len(rows), months)
                    opening = D(principal)
                    principal_sum = D(0)
                    for month, row in enumerate(rows, 1):
                        self.assertEqual(set(row), {'month', 'payment', 'interest', 'principal', 'balance'})
                        self.assertIs(type(row['month']), int)
                        self.assertEqual(row['month'], month)
                        for key in ('payment', 'interest', 'principal', 'balance'):
                            self.assertIsInstance(row[key], D)
                            self.assertEqual(row[key].as_tuple().exponent, -2)
                        interest = (opening * (D(rate) / 1200)).quantize(D('.01'))
                        self.assertEqual(row['interest'], interest)
                        self.assertEqual(row['payment'], row['principal'] + interest)
                        self.assertEqual(row['balance'], opening - row['principal'])
                        self.assertGreaterEqual(row['balance'], 0)
                        self.assertLessEqual(row['payment'], opening + interest)
                        opening = row['balance']
                        principal_sum += row['principal']
                    self.assertEqual(opening, D('0.00'))
                    self.assertEqual(principal_sum, D(principal))


if __name__ == '__main__':
    unittest.main()
