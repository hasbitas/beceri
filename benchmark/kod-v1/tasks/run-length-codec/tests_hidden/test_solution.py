import unittest

import solution


class CodecTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(solution.encode(''), '')
        self.assertEqual(solution.decode(''), '')

    def test_exact_encodings(self):
        cases = [
            ('a', '1a'), ('abc', '1a1b1c'), ('aaaa', '4a'),
            ('aaabbbbbbbbbbbbC', '3a12b1C'),
            ('aAAaaA', '1a2A2a1A'),
            ('ZZzzZZ', '2Z2z2Z'),
            ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
             ''.join('1' + c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')),
        ]
        for plain, encoded in cases:
            with self.subTest(encoded=encoded):
                self.assertEqual(solution.encode(plain), encoded)
                self.assertEqual(solution.decode(encoded), plain)

    def test_count_boundaries(self):
        for count in (1, 9, 10, 11, 99, 100, 101, 999, 1000, 99999, 100000):
            with self.subTest(count=count):
                self.assertEqual(solution.encode('q' * count), str(count) + 'q')
                self.assertEqual(solution.decode(str(count) + 'q'), 'q' * count)
        self.assertEqual(solution.decode('12a10B101z'), 'a' * 12 + 'B' * 10 + 'z' * 101)


    def test_non_string_arguments(self):
        for value in (None, 0, 1.5, True, b'1a', [], {}, ('a',)):
            for fn in (solution.encode, solution.decode):
                with self.subTest(fn=fn.__name__, value=value):
                    with self.assertRaises(TypeError):
                        fn(value)

    def test_invalid_plain_characters(self):
        for text in ('1', 'a1', 'a b', '\n', 'a\tb', 'a\x00b', 'é', 'Ω', 'Ａ', '🙂', 'a-b', 'a_b'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.encode(text)

    def test_leading_zero_counts(self):
        for encoded in ('01a', '001a', '010b', '000100A', '2a01b', '1A02a1B'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(ValueError):
                    solution.decode(encoded)

    def test_zero_and_missing_counts(self):
        for encoded in ('0a', '00a', '1a0b', 'a', 'abc', '1ab', 'a1b', '1aB'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(ValueError):
                    solution.decode(encoded)





if __name__ == '__main__':
    unittest.main()
