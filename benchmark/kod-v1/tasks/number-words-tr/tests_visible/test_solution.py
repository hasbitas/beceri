import contextlib
import io
import unittest

import solution


class TurkishNumberTests(unittest.TestCase):

    def test_all_two_digit_numbers(self):
        tens = ['on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan']
        units = ['', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz']
        for t, word in enumerate(tens, 1):
            for u, unit in enumerate(units):
                with self.subTest(t=t, u=u):
                    self.assertEqual(solution.to_words(t * 10 + u), word + (' ' + unit if u else ''))


    def test_single_thousand(self):
        cases = {
            1000: 'bin', 1001: 'bin bir', 1009: 'bin dokuz',
            1010: 'bin on', 1040: 'bin kırk', 1099: 'bin doksan dokuz',
            1100: 'bin yüz', 1101: 'bin yüz bir', 1111: 'bin yüz on bir',
            1500: 'bin beş yüz', 1999: 'bin dokuz yüz doksan dokuz',
        }
        for n, expected in cases.items():
            with self.subTest(n=n):
                self.assertEqual(solution.to_words(n), expected)



    def test_invalid_types(self):
        for value in (True, False, None, 1.0, 0.0, '123', b'1', [], {}, complex(1, 0)):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    solution.to_words(value)

    def test_out_of_range(self):
        for n in (-1, -1000, -10**30, 1000000, 1000001, 10**30):
            with self.subTest(n=n):
                with self.assertRaises(ValueError):
                    solution.to_words(n)



if __name__ == '__main__':
    unittest.main()
