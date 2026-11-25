import math
import unittest

import solution


class LengthTests(unittest.TestCase):
    def check_length(self, text, expected):
        actual = solution.to_meters(text)
        self.assertIsInstance(actual, float)
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                        (text, actual, expected))


    def test_compounds_and_order(self):
        for text, expected in [("5 ft 3 in", 1.6002), ("1cm1m", 1.01),
                               ("1yd2ft3in4m5cm6mm", 5.6562),
                               ("100in2ft", 3.1496), ("0m0cm0mm", 0.0)]:
            with self.subTest(text=text):
                self.check_length(text, expected)


    def test_whitespace_and_case(self):
        self.check_length(" \t\r\n+1\vFT\f2\tIN \r", 0.3556)
        self.check_length("1M\n2cM\r3Mm", 1.023)
        self.check_length("\v.5\fYd\t", 0.4572)


    def test_invalid_syntax(self):
        invalid = ["", " \n\t", "+", "-", "1", "m", "1 m 2", "1m junk",
                   "1meter", "1km", "1e3m", "1,5m", "1/2m", ".m", "1..2m",
                   "1m+2cm", "1m-2cm", "--1m", "+-1m", "- 1m", "+\t1m",
                   "1 m!", "1m_2cm", "NaNm", "infm", "1m\x00", "1 m s"]
        for text in invalid:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.to_meters(text)

    def test_repeated_units(self):
        for text in ["1m2m", "1CM2cm", "0ft0FT", "1m2cm3M", "1in 2IN"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.to_meters(text)





if __name__ == "__main__":
    unittest.main()
