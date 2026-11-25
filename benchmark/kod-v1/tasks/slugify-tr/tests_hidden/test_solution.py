import unittest

import solution


class SlugifyTests(unittest.TestCase):
    def check_cases(self, cases):
        for text, expected in cases:
            with self.subTest(text=text):
                result = solution.slugify(text)
                self.assertIsInstance(result, str)
                self.assertEqual(result, expected)



    def test_collapsed_separators(self):
        self.check_cases([
            (' -- A___ / B...C -- ', 'a-b-c'),
            ('one\t\n\r two\u00a0three', 'one-two-three'),
            ('a\x00\x01b', 'a-b'),
            ('a😀雪--/b', 'a-b'),
            ('a+b@c#d%20', 'a-b-c-d-20'),
        ])

    def test_empty_results(self):
        self.check_cases([
            ('', ''), (' ---___\t', ''), ('雪😀', ''),
            ('\u0301\u0307', ''), ('éßœæø', ''),
        ])

    def test_nfc_equivalence(self):
        self.check_cases([
            ('C\u0327 G\u0306 O\u0308 S\u0327 U\u0308', 'c-g-o-s-u'),
            ('c\u0327g\u0306o\u0308s\u0327u\u0308', 'cgosu'),
            ('I\u0307stanbul', 'istanbul'),
            ('cafe\u0301 noir', 'caf-noir'),
            ('q\u0307b', 'q-b'),
            ('Kilo', 'kilo'),
        ])

    def test_no_extra_transliteration_or_compatibility(self):
        self.check_cases([
            ('café déjà vu', 'caf-d-j-vu'),
            ('aßb æ œ ø ł', 'a-b'),
            ('xＡ１２３y', 'x-y'),
            ('xﬃy', 'x-y'),
            ('x١۲३y', 'x-y'),
            ('AΣБ中Z', 'a-z'),
        ])



    def test_long_input_and_idempotence(self):
        text = ('İÇ 00___' * 1500) + 'SON'
        expected = ('ic-00-' * 1500) + 'son'
        self.assertEqual(solution.slugify(text), expected)
        for value in ('İstanbul / 001', 'a--b', '', 'é/Ş', text):
            with self.subTest(length=len(value)):
                once = solution.slugify(value)
                self.assertEqual(solution.slugify(once), once)
                self.assertRegex(once, r'\A(?:[a-z0-9]+(?:-[a-z0-9]+)*)?\Z')


if __name__ == '__main__':
    unittest.main()
