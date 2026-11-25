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

    def test_interest_schedule_and_final_adjustment(self):
        self.assert_rows(solution.schedule(1000, 12, 3), [
            ('340.02', '10.00', '330.02', '669.98'),
            ('340.02', '6.70', '333.32', '336.66'),
            ('340.03', '3.37', '336.66', '0.00'),
        ])

    def test_zero_rate_residual(self):
        self.assert_rows(solution.schedule('100.00', 0, 3), [
            ('33.33', '0.00', '33.33', '66.67'),
            ('33.33', '0.00', '33.33', '33.34'),
            ('33.34', '0.00', '33.34', '0.00'),
        ])

    def test_final_payment_can_be_lower(self):
        self.assert_rows(solution.schedule('0.10', 0, 6), [
            ('0.02', '0.00', '0.02', '0.08'),
            ('0.02', '0.00', '0.02', '0.06'),
            ('0.02', '0.00', '0.02', '0.04'),
            ('0.02', '0.00', '0.02', '0.02'),
            ('0.02', '0.00', '0.02', '0.00'),
            ('0.00', '0.00', '0.00', '0.00'),
        ])


    def test_zero_regular_payment(self):
        self.assert_rows(solution.schedule('0.01', 0, 3), [
            ('0.00', '0.00', '0.00', '0.01'),
            ('0.00', '0.00', '0.00', '0.01'),
            ('0.01', '0.00', '0.01', '0.00'),
        ])

    def test_half_up_interest(self):
        self.assert_rows(solution.schedule(1, 6, 2), [
            ('0.50', '0.01', '0.49', '0.51'),
            ('0.51', '0.00', '0.51', '0.00'),
        ])


    def test_input_representations(self):
        expected = solution.schedule(1000, 12, 3)
        for principal in (1000.0, D('1000.000'), '  1e3  '):
            for rate in (12.0, D('12'), ' 12 '):
                with self.subTest(principal=principal, rate=rate):
                    self.assertEqual(solution.schedule(principal, rate, 3), expected)
        self.assertEqual(solution.schedule(0.1, 0.0, 6),
                         solution.schedule('0.10', '0', 6))


    def test_independent_of_decimal_context(self):
        expected = solution.schedule('123456.78', '4.125', 360)
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.rounding = ROUND_DOWN
            ctx.Emax = 9
            ctx.Emin = -9
            for signal in ctx.traps:
                ctx.traps[signal] = True
            ctx.clear_flags()
            before = (ctx.prec, ctx.rounding, ctx.Emax, ctx.Emin,
                      dict(ctx.traps), dict(ctx.flags))
            self.assertEqual(solution.schedule('123456.78', '4.125', 360), expected)
            for args in [('bad', 12, 3), ('1.001', 12, 3), (1, 'NaN', 3)]:
                with self.assertRaises(ValueError):
                    solution.schedule(*args)
            after = (ctx.prec, ctx.rounding, ctx.Emax, ctx.Emin,
                     dict(ctx.traps), dict(ctx.flags))
            self.assertEqual(before, after)



if __name__ == '__main__':
    unittest.main()
