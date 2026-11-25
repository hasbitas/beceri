import itertools
import unittest

import solution


class SplitCsvLineTests(unittest.TestCase):
    def check_cases(self, cases):
        for text, expected in cases:
            with self.subTest(text=text):
                result = solution.split_csv_line(text)
                self.assertIsInstance(result, list)
                self.assertEqual(result, expected)
                self.assertTrue(all(isinstance(field, str) for field in result))



    def test_quotes_and_commas(self):
        self.check_cases([('""', ['']), ('"a,b",c', ['a,b', 'c']),
                          ('a,"b,c",""', ['a', 'b,c', '']),
                          ('",,,"', [',,,']),
                          ('"a","b"', ['a', 'b'])])

    def test_escaped_quotes(self):
        self.check_cases([('""""', ['"']),
                          ('""""""', ['""']),
                          ('"a""b",x', ['a"b', 'x']),
                          ('"""start","end"""', ['"start', 'end"']),
                          ('"a,""b"",c"', ['a,"b",c'])])

    def test_literal_characters(self):
        self.check_cases([(' a ,\tb\t, ', [' a ', '\tb\t', ' ']),
                          ('" a \t",é,你好,🙂', [' a \t', 'é', '你好', '🙂']),
                          ('a\\b,"c\\d",\x00', ['a\\b', 'c\\d', '\x00']),
                          ('a\u2028b', ['a\u2028b'])])




    def test_generated_valid_records(self):
        values = ['', 'x', ',', 'a"b', ' ', 'é', '\\']
        # Construct valid spellings from decoded values, independently of parsing.
        for fields in itertools.product(values, repeat=3):
            for quote_all in (False, True):
                encoded = []
                for field in fields:
                    if quote_all or ',' in field or '"' in field:
                        encoded.append('"' + field.replace('"', '""') + '"')
                    else:
                        encoded.append(field)
                text = ','.join(encoded)
                with self.subTest(text=text):
                    self.assertEqual(solution.split_csv_line(text), list(fields))


if __name__ == '__main__':
    unittest.main()
