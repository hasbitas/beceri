import unittest

import solution


class ParseDurationTests(unittest.TestCase):
    def assert_invalid(self, values):
        for text in values:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.parse_duration(text)

    def test_examples_and_units(self):
        for text, expected in [
            ("1h30m15s", 5415), ("45s", 45), ("2d3s", 172803),
            ("1d", 86400), ("1h", 3600), ("1m", 60), ("1s", 1),
            ("1d2h3m4s", 93784), ("2d4m", 173040),
        ]:
            with self.subTest(text=text):
                result = solution.parse_duration(text)
                self.assertIs(type(result), int)
                self.assertEqual(result, expected)




    def test_invalid_grammar(self):
        self.assert_invalid([
            "", " \t\n", "s", "123", "1h30", "1", "1hs", "1hms",
            "+1s", "-1s", "1.5h", "1e3s", "1_000s", "1H", "1M", "1S",
            "1w", "1ms", "1 h", "1h 2m", "1h\t2m", "1h\n2s",
            "1\u00a0s", "١s", "１s", "²s", "1h٢m", "prefix1s",
            "1ssuffix", "1s!", "1s\x00", "1s\n2m", "1s,2s", "1s/2s",
        ])


    def test_out_of_order_nonzero_units(self):
        self.assert_invalid(["1s1m", "1m1h", "1h1d", "1d1s1h", "1m1d"])


    def test_out_of_order_zero_units(self):
        self.assert_invalid([
            "0s1m", "1s0m", "0m0h", "0h1d", "1m0d",
            "1d0s1h", "0d0s0m", "1h0s1m",
        ])


if __name__ == "__main__":
    unittest.main()
