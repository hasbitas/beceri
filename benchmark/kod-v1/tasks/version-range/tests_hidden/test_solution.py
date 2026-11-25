import unittest

import solution


class VersionRangeTests(unittest.TestCase):
    def check(self, version, spec, expected):
        self.assertIs(solution.satisfies(version, spec), expected)

    def test_combined_ranges(self):
        for version, expected in [("1.2", True), ("1.4", True),
                                  ("1.5", False), ("2.0", False),
                                  ("0.9", False)]:
            with self.subTest(version=version):
                self.check(version, ">=1.2,<2.0,!=1.5", expected)
        self.check("3", ">4,<2", False)
        self.check("3", ">=3,<=3,==3,!=4", True)

    def test_numeric_component_order(self):
        self.check("1.10", ">1.2", True)
        self.check("10.1", ">2.99", True)
        self.check("1.2.9", "<1.3", True)
        self.check("0001.00002", "==1.2", True)
        self.check("1.2.3.4.5.6.7", ">1.2.3.4.5.6.6", True)

    def test_zero_extension_equality(self):
        for left, right in [("1", "1.0"), ("1.0.0", "01"),
                            ("0", "00.0.0"), ("1.2", "1.2.0.0")]:
            for version, target in [(left, right), (right, left)]:
                with self.subTest(version=version, target=target):
                    self.check(version, target, True)
                    self.check(version, "==" + target, True)
                    self.check(version, "!=" + target, False)




    def test_invalid_specifications(self):
        invalid = [",", "1,", ",1", "1,,2", "1, \t ,2", ">=", "!= ",
                   "=1", "===1", "=>1", "=<1", "<>1", "~1", "^1",
                   "> =1", "! =1", "1 2", ">1. 2", ">=+1", "==١",
                   "1.*", "1-2", ">=1 <2", "1||2", "\u00a01"]
        for spec in invalid:
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    solution.satisfies("1", spec)

    def test_all_constraints_are_validated(self):
        for spec in [">99,=1", "<0,", "!=1,>=", ">99,1..2"]:
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    solution.satisfies("1", spec)
        with self.assertRaises(ValueError):
            solution.satisfies("bad", "")


    def test_large_components(self):
        huge = "9" * 5000
        self.check(huge, ">" + "8" * 5000, True)
        self.check("000" + huge, "==" + huge, True)

    def test_calls_are_independent(self):
        for _ in range(3):
            self.check("1.5", ">=1,<2", True)
            self.check("1.5", "!=1.5", False)
            self.check("1.5", "", True)


if __name__ == "__main__":
    unittest.main()
