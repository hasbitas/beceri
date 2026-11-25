import unittest

import solution


class ParseDurationTests(unittest.TestCase):
    def assert_invalid(self, values):
        for text in values:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.parse_duration(text)


    def test_whitespace_and_leading_zeros(self):
        for text, expected in [
            (" \t1h2s\n", 3602), ("\u20031m\u00a0", 60),
            ("0002h0003m0004s", 7384), ("000s", 0),
            ("0d0h0m0s", 0), ("0d2h0m5s", 7205),
        ]:
            with self.subTest(text=text):
                self.assertEqual(solution.parse_duration(text), expected)

    def test_unrestricted_magnitudes(self):
        for text, expected in [
            ("90m", 5400), ("100h120m999s", 368199),
            ("99999999999999999999s", 10**20 - 1),
        ]:
            with self.subTest(text=text):
                self.assertEqual(solution.parse_duration(text), expected)
        self.assertEqual(solution.parse_duration("1" + "0" * 5000 + "s"), 10**5000)
        self.assertEqual(solution.parse_duration("9" * 5000 + "m1s"), (10**5000 - 1) * 60 + 1)

    def test_non_string_inputs(self):
        for value in [None, True, False, 0, 45, 1.5, b"45s", [], {}, ("1s",)]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.parse_duration(value)


    def test_duplicate_nonzero_units(self):
        self.assert_invalid(["1s2s", "1h2h", "1d2d", "1m2m", "1h2m3h"])


    def test_duplicate_zero_units(self):
        self.assert_invalid([
            "0s0s", "0h1h", "1h0h", "0d0d", "0m00m",
            "1d0h0h1s", "0d0h0m0s0s", "1h0m1m",
        ])



if __name__ == "__main__":
    unittest.main()
