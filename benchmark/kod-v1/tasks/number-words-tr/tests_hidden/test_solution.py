import contextlib
import io
import unittest

import solution


class TurkishNumberTests(unittest.TestCase):
    def test_units_and_zero(self):
        expected = ['sıfır', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz']
        for n, word in enumerate(expected):
            with self.subTest(n=n):
                self.assertEqual(solution.to_words(n), word)


    def test_all_hundreds(self):
        prefixes = ['yüz', 'iki yüz', 'üç yüz', 'dört yüz', 'beş yüz', 'altı yüz', 'yedi yüz', 'sekiz yüz', 'dokuz yüz']
        # The independent tests above establish all possible two-digit suffixes.
        for h, prefix in enumerate(prefixes, 1):
            for r in range(100):
                with self.subTest(h=h, r=r):
                    expected = prefix if r == 0 else prefix + ' ' + solution.to_words(r)
                    self.assertEqual(solution.to_words(100 * h + r), expected)


    def test_thousand_groups(self):
        for q in range(2, 1000):
            for r in (0, 1, 9, 10, 42, 100, 101, 110, 505, 999):
                with self.subTest(q=q, r=r):
                    expected = solution.to_words(q) + ' bin'
                    if r:
                        expected += ' ' + solution.to_words(r)
                    self.assertEqual(solution.to_words(q * 1000 + r), expected)

    def test_fixed_large_examples(self):
        cases = {
            10000: 'on bin', 11000: 'on bir bin', 21001: 'yirmi bir bin bir',
            100000: 'yüz bin', 100001: 'yüz bin bir',
            101000: 'yüz bir bin', 101100: 'yüz bir bin yüz',
            111111: 'yüz on bir bin yüz on bir',
            200200: 'iki yüz bin iki yüz',
            406708: 'dört yüz altı bin yedi yüz sekiz',
            999999: 'dokuz yüz doksan dokuz bin dokuz yüz doksan dokuz',
        }
        for n, expected in cases.items():
            with self.subTest(n=n):
                self.assertEqual(solution.to_words(n), expected)



    def test_subclass_repeatability_and_silence(self):
        class MyInt(int):
            pass

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            for _ in range(3):
                for n, expected in ((123, 'yüz yirmi üç'), (0, 'sıfır'), (1000, 'bin'), (6, 'altı')):
                    result = solution.to_words(MyInt(n))
                    self.assertIsInstance(result, str)
                    self.assertEqual(result, expected)
                    self.assertEqual(result, ' '.join(result.split()))
        self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
