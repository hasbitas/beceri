import unittest

import solution


class FormatTryTests(unittest.TestCase):


    def test_group_boundaries(self):
        for cents, expected in [(99999, '999,99 TL'),
                                (100000, '1.000,00 TL'),
                                (100001, '1.000,01 TL'),
                                (99999999, '999.999,99 TL'),
                                (100000000, '1.000.000,00 TL'),
                                (100000001, '1.000.000,01 TL')]:
            with self.subTest(cents=cents):
                self.assertEqual(solution.format_try(cents), expected)

    def test_negative_amounts(self):
        for cents, expected in [(-1, '-0,01 TL'), (-5, '-0,05 TL'),
                                (-99, '-0,99 TL'), (-100, '-1,00 TL'),
                                (-101, '-1,01 TL'),
                                (-123456, '-1.234,56 TL'),
                                (-100000001, '-1.000.000,01 TL')]:
            with self.subTest(cents=cents):
                self.assertEqual(solution.format_try(cents), expected)



    def test_arbitrary_integer_magnitude(self):
        amount = (1000 ** 1700 - 1) * 100 + 99
        expected = '.'.join(['999'] * 1700) + ',99 TL'
        self.assertEqual(solution.format_try(amount), expected)
        self.assertEqual(solution.format_try(-amount), '-' + expected)


if __name__ == '__main__':
    unittest.main()
