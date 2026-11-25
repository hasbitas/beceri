import math
import unittest

import solution


class LengthTests(unittest.TestCase):
    def check_length(self, text, expected):
        actual = solution.to_meters(text)
        self.assertIsInstance(actual, float)
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                        (text, actual, expected))

    def test_unit_factors(self):
        for text, expected in [("1m", 1.0), ("12cm", 0.12), ("7mm", 0.007),
                               ("1in", 0.0254), ("1ft", 0.3048), ("1yd", 0.9144),
                               ("1.5 m", 1.5)]:
            with self.subTest(text=text):
                self.check_length(text, expected)


    def test_decimal_forms(self):
        for text, expected in [(".5M2.cm", 0.52), ("00012.50cm", 0.125),
                               ("5.ft", 1.524), (".001m", 0.001),
                               ("0.mm", 0.0), ("01.00m.5cm", 1.005)]:
            with self.subTest(text=text):
                self.check_length(text, expected)


    def test_sign_applies_to_whole_sum(self):
        for text, expected in [("-1ft6in", -0.4572), ("-0m5cm", -0.05),
                               ("-2cm1m", -1.02), ("-1yd2ft3in", -1.6002),
                               ("+1ft6in", 0.4572), ("-12cm", -0.12),
                               ("-0mm", 0.0)]:
            with self.subTest(text=text):
                self.check_length(text, expected)



    def test_non_ascii_rejected(self):
        for text in ["١m", "１m", "1\u00a0m", "\u20031m", "1m\u00a0",
                     "1m\u20032cm", "1İN", "−1m"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.to_meters(text)

    def test_wrong_types(self):
        for value in [None, 1, 1.5, True, b"1m", [], {}, ("1m",)]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.to_meters(value)

    def test_float_range(self):
        self.check_length("1" + "0" * 309 + "mm", 1e306)
        self.check_length("0." + "0" * 400 + "1m", 0.0)
        for text in ["9" * 400 + "m", "-" + "9" * 400 + "mm",
                     "1" + "0" * 308 + "m" + "9" + "0" * 309 + "cm"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.to_meters(text)


if __name__ == "__main__":
    unittest.main()
