import unittest

import solution


class ConversionTests(unittest.TestCase):


    def test_all_bases_and_digits(self):
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        for source in range(2, 37):
            for value in range(source):
                for target in range(2, 37):
                    # Independently form this bounded value's target spelling.
                    n = value
                    expected = ""
                    while n:
                        expected = alphabet[n % target] + expected
                        n //= target
                    expected = expected or "0"
                    with self.subTest(source=source, target=target, value=value):
                        self.assertEqual(solution.convert(alphabet[value].upper(), source, target), expected)
            for digit in alphabet[source:]:
                with self.subTest(source=source, digit=digit):
                    with self.assertRaises(ValueError):
                        solution.convert("10" + digit.upper(), source, 10)


    def test_prefixes_are_not_special(self):
        for text, base in [("0b10", 2), ("-0B1", 2), ("0o10", 8),
                           ("+0O7", 8), ("0x10", 16), ("-0Xf", 16)]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.convert(text, base, 10)
        self.assertEqual(solution.convert("0b10", 12, 10), "1596")

    def test_argument_types(self):
        for bad in (None, True, 12, 1.5, b"10", ["1", "0"], {"x": 1}):
            with self.subTest(text=bad):
                with self.assertRaises(TypeError):
                    solution.convert(bad, 10, 2)
        for bad in (None, True, False, 10.0, "10", [], complex(2, 0)):
            for position in (0, 1):
                bases = [10, 10]
                bases[position] = bad
                with self.subTest(base=bad, position=position):
                    with self.assertRaises(TypeError):
                        solution.convert("10", *bases)

    def test_base_range(self):
        for bad in (-100, -2, 0, 1, 37, 100):
            for source, target in ((bad, 10), (10, bad)):
                with self.subTest(source=source, target=target):
                    with self.assertRaises(ValueError):
                        solution.convert("0", source, target)

    def test_large_exact_values(self):
        self.assertEqual(solution.convert("f" * 100, 16, 2), "1" * 400)
        self.assertEqual(solution.convert("-" + "1" * 400, 2, 16), "-" + "f" * 100)
        decimal = "1" + "0" * 4500
        self.assertEqual(solution.convert(decimal, 10, 10), decimal)
        self.assertEqual(solution.convert("-" + decimal, 10, 10), "-" + decimal)
        self.assertEqual(solution.convert("0" * 5000 + "42", 10, 16), "2a")
        binary = "1" + "0" * 8192
        self.assertEqual(solution.convert(binary, 2, 16), "1" + "0" * 2048)


if __name__ == "__main__":
    unittest.main()
