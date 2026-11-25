import unittest

import solution


class VersionRangeTests(unittest.TestCase):
    def check(self, version, spec, expected):
        self.assertIs(solution.satisfies(version, spec), expected)




    def test_zero_extension_boundaries(self):
        for op, expected in [("<", False), (">", False),
                             ("<=", True), (">=", True)]:
            self.check("2", op + "2.0.0", expected)
            self.check("2.0.0", op + "2", expected)
        self.check("2.0.0.1", ">2", True)
        self.check("2", "<2.0.0.1", True)

    def test_whitespace_and_bare_equality(self):
        self.check(" \t01.2\r\n", "\v >= \t1.2 , < 2 , 01.2 \f", True)
        self.check("1.2", " 1.3 ", False)
        self.check("0", "", True)
        self.check("999.0.2", " \t\r\n\v\f", True)

    def test_invalid_versions(self):
        invalid = ["", " ", ".1", "1.", "1..2", "-1", "+1", "1e2",
                   "1.2rc1", "v1", "1_0", "1 2", "1. 2", "1\t.2",
                   "١", "１.2", "1\x00", "\u00a01"]
        for version in invalid:
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    solution.satisfies(version, "")



    def test_argument_types(self):
        for value in [None, 1, 1.2, True, b"1", [], {}]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.satisfies(value, "")
                with self.assertRaises(TypeError):
                    solution.satisfies("1", value)
        with self.assertRaises(TypeError):
            solution.satisfies("bad", None)




if __name__ == "__main__":
    unittest.main()
