import unittest

import solution


class SlugifyTests(unittest.TestCase):
    def check_cases(self, cases):
        for text, expected in cases:
            with self.subTest(text=text):
                result = solution.slugify(text)
                self.assertIsInstance(result, str)
                self.assertEqual(result, expected)

    def test_ascii_and_digits(self):
        self.check_cases([
            ('Hello WORLD 2026', 'hello-world-2026'),
            ('00042 A1B2', '00042-a1b2'),
            ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),
            ('aabb0099', 'aabb0099'),
        ])

    def test_turkish_letters(self):
        self.check_cases([
            ('çğıiöşü', 'cgiiosu'),
            ('ÇĞIİÖŞÜ', 'cgiiosu'),
            ('İstanbul İzmir Iğdır', 'istanbul-izmir-igdir'),
            ('Türkçe: Çılgın Şöför, GÜNEŞ!', 'turkce-cilgin-sofor-gunes'),
            ('aİb', 'aib'),
            ('İİ', 'ii'),
        ])





    def test_invalid_types(self):
        for value in (None, 123, 1.5, True, b'hello', [], {}, ('x',)):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.slugify(value)

    def test_str_subclass(self):
        class Text(str):
            pass
        self.assertEqual(solution.slugify(Text('Çay SAATİ')), 'cay-saati')



if __name__ == '__main__':
    unittest.main()
