import itertools
import unittest

import solution


# Indexed by the original digit, the doubled-and-reduced contribution.
DOUBLED = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)


def oracle_valid(text):
    contributions = []
    for index, char in enumerate(text):
        digit = ord(char) - ord('0')
        contributions.append(DOUBLED[digit] if (len(text) - index) % 2 == 0 else digit)
    return bool(text) and sum(contributions) % 10 == 0


class LuhnTests(unittest.TestCase):

    def test_known_check_digits(self):
        for payload, expected in (('0', '0'), ('1', '8'), ('5', '9'), ('12', '5'),
                                  ('7992739871', '3'), ('453201511283036', '6'),
                                  ('0001', '8')):
            with self.subTest(payload=payload):
                result = solution.luhn_check_digit(payload)
                self.assertIs(type(result), str)
                self.assertEqual(result, expected)


    def test_no_digits(self):
        for text in ('', ' ', '-', ' -- -  '):
            with self.subTest(text=text):
                self.assertIs(solution.luhn_valid(text), False)
                with self.assertRaises(ValueError):
                    solution.luhn_check_digit(text)


    def test_non_strings(self):
        for value in (None, 0, 123, True, 1.2, b'18', bytearray(b'18'), ['1', '8'], {}):
            for function in (solution.luhn_valid, solution.luhn_check_digit):
                with self.subTest(value=value, function=function.__name__):
                    with self.assertRaises(TypeError):
                        function(value)


    def test_bounded_payloads(self):
        for width in range(1, 4):
            for chars in itertools.product('0159', repeat=width):
                payload = ''.join(chars)
                expected = next(str(d) for d in range(10) if oracle_valid(payload + str(d)))
                with self.subTest(payload=payload):
                    self.assertEqual(solution.luhn_check_digit(payload), expected)

    def test_long_inputs_and_leading_zeros(self):
        for payload in ('0' * 6000, '0' * 6001 + '1', '1234567890' * 601):
            expected = next(str(d) for d in range(10) if oracle_valid(payload + str(d)))
            with self.subTest(length=len(payload), suffix=payload[-10:]):
                self.assertEqual(solution.luhn_check_digit(payload), expected)
                self.assertIs(solution.luhn_valid(payload + expected), True)
                self.assertIs(solution.luhn_valid(payload + str((int(expected) + 1) % 10)), False)


if __name__ == '__main__':
    unittest.main()
