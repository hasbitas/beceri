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





    def test_letters_throughout_body(self):
        for country, body in (
            ('AA', 'ABCDEFGHIJK'),
            ('QZ', 'ZYXWVUTSRQPONMLKJIHGFEDCBA'),
            ('XX', '0A0Z00000000000000000000000001'),
            ('AB', '00000000000'),
        ):
            with self.subTest(country=country, body=body):
                self.assert_valid(make_iban(country, body))

    def test_invalid_structure(self):
        base = 'GB82WEST12345698765432'
        for text in ('1' + base[1:], base[0] + '2' + base[2:],
                     base[:2] + 'A' + base[3:], base[:3] + 'B' + base[4:]):
            self.assert_invalid(text)
        for char in ('-', '.', '_', '/', '+', '\x00', '\u00df', '\u0131',
                     '\uff11', '\u0661', '\u212a', '\u00e9'):
            with self.subTest(char=char):
                self.assert_invalid(base[:8] + char + base[9:])
        self.assert_invalid('\uff27' + base[1:])

    def test_bad_checksums(self):
        base = 'GB82WEST12345698765432'
        for position in range(4, len(base)):
            char = base[position]
            replacement = '0' if char != '0' else '1'
            with self.subTest(position=position):
                self.assert_invalid(base[:position] + replacement + base[position + 1:])
        self.assert_invalid('GB83' + base[4:])

    def test_check_digit_range_even_when_modulo_matches(self):
        for check in ('00', '01', '99'):
            for number in range(1000):
                text = 'ZZ' + check + f'{number:011d}'
                if expanded_number(text) % 97 == 1:
                    break
            else:
                self.fail('No deterministic checksum fixture found')
            self.assert_invalid(text)
        for check in (2, 98):
            for number in range(1000):
                text = 'ZZ' + f'{check:02d}' + f'{number:011d}'
                if expanded_number(text) % 97 == 1:
                    break
            else:
                self.fail('No deterministic checksum fixture found')
            self.assert_valid(text)



if __name__ == '__main__':
    unittest.main()
