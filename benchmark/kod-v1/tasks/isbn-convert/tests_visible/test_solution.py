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

    def test_zero_check_and_leading_zero_bodies(self):
        for body in ("000000000", "000000014", "123456789", "000000001"):
            with self.subTest(body=body):
                ten, thirteen = isbn10(body), isbn13("978" + body)
                self.assertEqual(solution.isbn10_to_13(ten), thirteen)
                self.assertEqual(solution.isbn13_to_10(thirteen), ten)


    def test_separators_and_lowercase_x(self):
        self.assertEqual(solution.isbn10_to_13(" -0 804-42957-x- "), "9780804429573")
        self.assertEqual(solution.isbn13_to_10("- 978--0 804 42957-3 -"), "080442957X")
        self.assertEqual(solution.isbn10_to_13(" - ".join("0306406152")), "9780306406157")

    def test_every_wrong_checksum(self):
        for body in ("030640615", "080442957", "000000000"):
            valid = isbn10(body)
            for digit in "0123456789Xx":
                if digit.upper() != valid[-1]:
                    with self.subTest(body=body, digit=digit):
                        with self.assertRaises(ValueError):
                            solution.isbn10_to_13(body + digit)
            valid13 = isbn13("978" + body)
            for digit in "0123456789":
                if digit != valid13[-1]:
                    with self.assertRaises(ValueError):
                        solution.isbn13_to_10(valid13[:-1] + digit)





if __name__ == "__main__":
    unittest.main()
