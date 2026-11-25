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
    def test_known_complete_numbers(self):
        for number in ('0', '00', '18', '59', '79927398713', '4532015112830366'):
            with self.subTest(number=number):
                self.assertIs(solution.luhn_valid(number), True)
        for number in ('1', '01', '10', '79927398714', '4532015112830367'):
            with self.subTest(number=number):
                self.assertIs(solution.luhn_valid(number), False)


    def test_separator_placement(self):
        for raw in ('0', '18', '123', '7992739871', '000001'):
            decorated = ' --' + ' -  --'.join(raw) + '-- '
            with self.subTest(raw=raw):
                self.assertIs(solution.luhn_valid(decorated), oracle_valid(raw))
                expected = next(str(d) for d in range(10) if oracle_valid(raw + str(d)))
                self.assertEqual(solution.luhn_check_digit(decorated), expected)
                self.assertIs(solution.luhn_valid(decorated + expected + ' -'), True)


    def test_invalid_characters(self):
        for text in ('\t', '\n', '\r', '\v', '\f', '\u00a0', '１２', '١٢', '²',
                     '+12', '12.0', '1_2', '1–2', '12x', ' --x', '0\x00', '0\n'):
            for function in (solution.luhn_valid, solution.luhn_check_digit):
                with self.subTest(text=text, function=function.__name__):
                    with self.assertRaises(ValueError):
                        function(text)


    def test_bounded_complete_numbers(self):
        for width in range(1, 4):
            for chars in itertools.product('0123456789', repeat=width):
                text = ''.join(chars)
                with self.subTest(text=text):
                    self.assertIs(solution.luhn_valid(text), oracle_valid(text))




if __name__ == '__main__':
    unittest.main()
