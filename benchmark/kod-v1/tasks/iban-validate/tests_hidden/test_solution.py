import unittest

import solution


def expanded_number(text):
    return int(''.join(str(ord(c) - 55) if 'A' <= c <= 'Z' else c
                       for c in text[4:] + text[:4]))


def make_iban(country, body):
    candidate = country + '00' + body
    check = 98 - expanded_number(candidate) % 97
    return country + f'{check:02d}' + body


class IbanValidationTests(unittest.TestCase):
    def assert_valid(self, text):
        self.assertIs(solution.iban_valid(text), True, repr(text))

    def assert_invalid(self, text):
        self.assertIs(solution.iban_valid(text), False, repr(text))

    def test_known_valid_accounts(self):
        for text in (
            'GB82WEST12345698765432',
            'DE89370400440532013000',
            'FR1420041010050500013M02606',
            'NL91ABNA0417164300',
            'NO9386011117947',
            'CH9300762011623852957',
        ):
            with self.subTest(text=text):
                self.assert_valid(text)

    def test_case_and_ascii_spaces(self):
        original = 'GB82WEST12345698765432'
        for text in (original.lower(), '  gB82 WeSt 1234 5698 7654 32  ',
                     ' '.join(original.lower()), '   ' + original + '   '):
            with self.subTest(text=text):
                self.assert_valid(text)

    def test_other_whitespace_is_not_ignored(self):
        base = 'GB82WEST12345698765432'
        for whitespace in ('\t', '\n', '\r', '\v', '\f', '\u00a0', '\u2003'):
            for text in (whitespace + base, base + whitespace,
                         base[:8] + whitespace + base[8:]):
                with self.subTest(text=text):
                    self.assert_invalid(text)

    def test_length_boundaries_and_unknown_countries(self):
        for length in (15, 16, 27, 33, 34):
            text = make_iban('ZZ', '0' * (length - 5) + '1')
            with self.subTest(length=length):
                self.assert_valid(text)
                self.assert_valid(' '.join(text))
        for length in (5, 14, 35, 60):
            self.assert_invalid(make_iban('ZZ', '0' * (length - 5) + '1'))
        self.assert_invalid('')
        self.assert_invalid('    ')





    def test_non_string_inputs(self):
        for value in (None, False, True, 0, 123, 1.5,
                      b'GB82WEST12345698765432', [], {}, ['GB82WEST12345698765432']):
            with self.subTest(value=value):
                self.assert_invalid(value)


if __name__ == '__main__':
    unittest.main()
