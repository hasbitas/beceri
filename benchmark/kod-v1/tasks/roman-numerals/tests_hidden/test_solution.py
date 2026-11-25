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


    def test_exhaustive_decoding(self):
        for value in range(1, 4000):
            with self.subTest(value=value):
                actual = solution.from_roman(CANONICAL[value])
                self.assertIs(type(actual), int)
                self.assertEqual(actual, value)

    def test_exhaustive_round_trip(self):
        for value in range(1, 4000):
            self.assertEqual(solution.from_roman(solution.to_roman(value)), value)

    def test_integer_range(self):
        for value in (-10**100, -4000, -1, 0, 4000, 4001, 10**100):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    solution.to_roman(value)


    def test_string_types(self):
        for value in (True, False, None, 1, 4.0, b'IV', bytearray(b'IV'), ['I'], {}, ('I',)):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    solution.from_roman(value)

    def test_lexical_rejection(self):
        for text in ('', ' ', 'iv', 'Iv', 'mCm', ' IV', 'IV ', 'I V',
                     '\tX', 'X\n', 'X\r\n', 'I\x00', 'X\u00a0',
                     'Ⅳ', 'ＩＶ', 'Χ', '1', '+V', 'X!', 'ABC'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.from_roman(text)


    def test_all_short_symbol_sequences(self):
        valid = {text: value for value, text in enumerate(CANONICAL) if value}
        for length in range(1, 5):
            for chars in itertools.product('IVXLCDM', repeat=length):
                text = ''.join(chars)
                with self.subTest(text=text):
                    if text in valid:
                        self.assertEqual(solution.from_roman(text), valid[text])
                    else:
                        with self.assertRaises(ValueError):
                            solution.from_roman(text)


if __name__ == '__main__':
    unittest.main()
