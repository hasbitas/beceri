import itertools
import unittest

import solution


THOUSANDS = ('', 'M', 'MM', 'MMM')
HUNDREDS = ('', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM')
TENS = ('', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC')
UNITS = ('', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX')
CANONICAL = tuple(a + b + c + d for a in THOUSANDS for b in HUNDREDS
                  for c in TENS for d in UNITS)


class RomanTests(unittest.TestCase):
    def test_known_conversions(self):
        for value, text in ((1, 'I'), (4, 'IV'), (9, 'IX'), (40, 'XL'),
                            (49, 'XLIX'), (90, 'XC'), (400, 'CD'),
                            (944, 'CMXLIV'), (1984, 'MCMLXXXIV'),
                            (2026, 'MMXXVI'), (3999, 'MMMCMXCIX')):
            with self.subTest(value=value):
                self.assertEqual(solution.to_roman(value), text)
                self.assertEqual(solution.from_roman(text), value)

    def test_exhaustive_encoding(self):
        for value in range(1, 4000):
            with self.subTest(value=value):
                actual = solution.to_roman(value)
                self.assertIsInstance(actual, str)
                self.assertEqual(actual, CANONICAL[value])




    def test_integer_types(self):
        for value in (True, False, None, 1.0, 3999.0, '4', b'4', [], {}, (1,), 1j):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    solution.to_roman(value)



    def test_noncanonical_forms(self):
        for text in ('IIII', 'VV', 'XXXX', 'LL', 'CCCC', 'DD', 'MMMM',
                     'VX', 'IL', 'IC', 'ID', 'IM', 'XD', 'XM', 'LC', 'DM',
                     'IIV', 'IIX', 'XXC', 'CCD', 'VIV', 'IXIX', 'XLX',
                     'CMC', 'MCMC', 'IVI', 'IXV', 'MIM', 'MMMDCCCCLXXXXVIIII'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.from_roman(text)



if __name__ == '__main__':
    unittest.main()
