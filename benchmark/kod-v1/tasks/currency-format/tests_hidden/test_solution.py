import unittest

import solution


class FormatTryTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(solution.format_try(0), '0,00 TL')

    def test_small_amounts(self):
        for cents, expected in [(1, '0,01 TL'), (5, '0,05 TL'),
                                (10, '0,10 TL'), (99, '0,99 TL'),
                                (100, '1,00 TL'), (101, '1,01 TL')]:
            with self.subTest(cents=cents):
                self.assertEqual(solution.format_try(cents), expected)



    def test_internal_zero_groups(self):
        self.assertEqual(solution.format_try(100000200304), '1.000.002.003,04 TL')
        self.assertEqual(solution.format_try(-100000000007), '-1.000.000.000,07 TL')
        self.assertEqual(solution.format_try(123456), '1.234,56 TL')

    def test_large_exact_amounts(self):
        amount = 12345678901234567890123456789
        expected = '123.456.789.012.345.678.901.234.567,89 TL'
        self.assertEqual(solution.format_try(amount), expected)
        self.assertEqual(solution.format_try(-amount), '-' + expected)
        self.assertEqual(solution.format_try(9007199254740993),
                         '90.071.992.547.409,93 TL')



if __name__ == '__main__':
    unittest.main()
