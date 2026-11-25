import unittest

import solution


class ConversionTests(unittest.TestCase):
    def test_known_conversions(self):
        cases = [
            ("101101", 2, 10, "45"),
            ("255", 10, 16, "ff"),
            ("Zz", 36, 10, "1295"),
            ("777", 8, 2, "111111111"),
            ("deadBEEF", 16, 10, "3735928559"),
            ("0b10", 16, 10, "2832"),
            ("0X10", 36, 36, "x10"),
        ]
        for text, source, target, expected in cases:
            with self.subTest(text=text, source=source, target=target):
                actual = solution.convert(text, source, target)
                self.assertIsInstance(actual, str)
                self.assertEqual(actual, expected)

    def test_signs_and_canonicalization(self):
        for base in range(2, 37):
            for text, expected in [("0", "0"), ("-000", "0"),
                                   ("+000", "0"), ("0001", "1"),
                                   ("-0001", "-1"), ("+0010", "10")]:
                with self.subTest(base=base, text=text):
                    self.assertEqual(solution.convert(text, base, base), expected)
        self.assertEqual(solution.convert("-000AbC", 16, 16), "-abc")
        self.assertEqual(solution.convert("-1295", 10, 36), "-zz")
        self.assertEqual(solution.convert("+FF", 16, 2), "11111111")


    def test_malformed_text(self):
        cases = ["", "+", "-", "--1", "+-1", "-+1", "++1", "1-0", "1+0",
                 " 10", "10 ", "\t10", "10\n", "1 0", "1\t0", "1\n0",
                 "1_0", "_10", "10_", "1__0", "1.0", "1/0", "1\x000",
                 "１２", "١٠", "²", "Ａ", "é", "−1", "\u00a010"]
        for text in cases:
            for target in (10, 36):
                with self.subTest(text=text, target=target):
                    with self.assertRaises(ValueError):
                        solution.convert(text, 10, target)






if __name__ == "__main__":
    unittest.main()
