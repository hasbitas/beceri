import unittest

import solution


def isbn10(body):
    # Independent construction from the defining congruence.
    for check in range(11):
        if (sum(int(c) * (10 - i) for i, c in enumerate(body)) + check) % 11 == 0:
            return body + ("X" if check == 10 else str(check))
    raise AssertionError("No check digit")


def isbn13(body):
    for check in range(10):
        if (sum(int(c) * (1, 3)[i % 2] for i, c in enumerate(body)) + check) % 10 == 0:
            return body + str(check)
    raise AssertionError("No check digit")


class ConversionTests(unittest.TestCase):
    def test_known_examples(self):
        pairs = [("0306406152", "9780306406157"),
                 ("0131103628", "9780131103627"),
                 ("080442957X", "9780804429573")]
        for ten, thirteen in pairs:
            with self.subTest(ten=ten):
                self.assertEqual(solution.isbn10_to_13(ten), thirteen)
                self.assertEqual(solution.isbn13_to_10(thirteen), ten)


    def test_all_check_digits_and_deterministic_bodies(self):
        for number in range(220):
            body = str(number * 4321091 % 1000000000).zfill(9)
            with self.subTest(body=body):
                ten, thirteen = isbn10(body), isbn13("978" + body)
                self.assertEqual(solution.isbn10_to_13(ten), thirteen)
                self.assertEqual(solution.isbn13_to_10(thirteen), ten)



    def test_invalid_formats(self):
        invalid10 = ["", " - ", "030640615", "00306406152", "X306406152",
                     "030640615?", "030640615２", "０306406152", "+0306406152",
                     "0306406152\n", "\t0306406152", "03064\r06152",
                     "03064\u00a006152", "03064\u201006152", "0306406152\x00"]
        invalid13 = ["", "978030640615", "97803064061570", "978030640615X",
                     "９780306406157", "978030640615７", "9780306406157\n",
                     "978\t0306406157", "978\u00a00306406157", "978/0306406157",
                     "978\u20110306406157", "9780306406157\x00"]
        for func, values in ((solution.isbn10_to_13, invalid10),
                             (solution.isbn13_to_10, invalid13)):
            for value in values:
                with self.subTest(value=value, function=func.__name__):
                    with self.assertRaises(ValueError):
                        func(value)

    def test_prefixes_and_nonconvertible_979(self):
        for prefix in ("000", "977", "980", "123", "979"):
            for body in ("000000000", "123456789"):
                value = isbn13(prefix + body)
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        solution.isbn13_to_10(value)
        with self.assertRaises(ValueError):
            solution.isbn13_to_10("9791234567890")

    def test_non_strings(self):
        for func in (solution.isbn10_to_13, solution.isbn13_to_10):
            for value in (None, 306406152, 9780306406157, 1.0, True,
                          b"0306406152", [], {}, ("0306406152",)):
                with self.subTest(function=func.__name__, value=value):
                    with self.assertRaises(TypeError):
                        func(value)


if __name__ == "__main__":
    unittest.main()
