import unittest

import solution


class CodecTests(unittest.TestCase):



    def test_round_trips(self):
        for text in ('ab' * 200, 'AaaAAbBBBba', 'z' * 500 + 'Z' * 400 + 'z', 'AbCdEf'):
            with self.subTest(text=text[:20]):
                encoded = solution.encode(text)
                self.assertEqual(solution.decode(encoded), text)
                self.assertEqual(solution.encode(solution.decode(encoded)), encoded)





    def test_truncated_and_separated_tokens(self):
        for encoded in ('1', '123', '1a2', '12a100', ' 1a', '1a ', '1 a', '1a\n',
                        '+1a', '-1a', '1.5a', '1a,2b', '1a\x002b', '1_a', '2!'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(ValueError):
                    solution.decode(encoded)

    def test_non_ascii_encoded_characters(self):
        for encoded in ('١a', '１a', '²a', '1١a', '1é', '2Ω', '3Ａ', '1🙂', '1a2é'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(ValueError):
                    solution.decode(encoded)

    def test_adjacent_equal_runs(self):
        for encoded in ('1a1a', '12A3A', '1b2a3a', '1a1A1A'):
            with self.subTest(encoded=encoded):
                with self.assertRaises(ValueError):
                    solution.decode(encoded)
        self.assertEqual(solution.decode('1a1A1a'), 'aAa')
        self.assertEqual(solution.decode('1a1b1a'), 'aba')


if __name__ == '__main__':
    unittest.main()
