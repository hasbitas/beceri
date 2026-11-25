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

    def test_plain_fields(self):
        self.check_cases([('alpha,beta,gamma', ['alpha', 'beta', 'gamma']),
                          ('one', ['one']), ('a;b|c', ['a;b|c'])])

    def test_empty_fields(self):
        self.check_cases([('', ['']), (',', ['', '']),
                          (',,,', ['', '', '', '']),
                          (',a,,b,', ['', 'a', '', 'b', '']),
                          ('a,', ['a', '']), ('"",', ['', '']),
                          ('"a,b",', ['a,b', ''])])




    def test_invalid_quote_placement(self):
        for text in ['"', '"abc', '"a""', 'a"b', 'a"',
                     ' "a"', '\t"a"', '"a" ', '"a"\t',
                     '"a"b', '""x', 'ok,"bad', 'ok,b"ad',
                     '"a";b', '"a\\"b"']:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.split_csv_line(text)

    def test_reject_record_terminators(self):
        for text in ['\n', '\r', '\r\n', 'a\n', 'a\r\n',
                     'a\nb', '"a\nb"', '"\r"', 'a,"b\r\nc"']:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.split_csv_line(text)

    def test_invalid_types(self):
        for value in [None, 0, True, b'a,b', ['a', 'b'], {'a': 1}]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.split_csv_line(value)



if __name__ == '__main__':
    unittest.main()
