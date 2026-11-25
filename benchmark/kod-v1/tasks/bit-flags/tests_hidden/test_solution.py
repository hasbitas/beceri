import unittest

import solution


class FlagTests(unittest.TestCase):


    def test_ordered_removal_and_readdition(self):
        cases = {
            "READ,!READ,READ": 1,
            "!READ,READ": 1,
            "ALL,!WRITE,!HIDDEN,WRITE": 23,
            "READ,WRITE,!ALL,ARCHIVE": 16,
            "ALL,!ALL,ALL": 31,
            "!ALL,ALL": 31,
            "ALL,!ALL": 0,
            "READ,!WRITE": 1,
            "ALL,!READ,!READ": 30,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(solution.parse_flags(text), expected)

    def test_unknown_names_and_invalid_syntax(self):
        invalid = (
            "read", "Read", "all", "none", "UNKNOWN", "READ,UNKNOWN",
            "ALL,!UNKNOWN", "UNKNOWN,!ALL", "READ WRITE", "READ|WRITE",
            ",", ",READ", "READ,", "READ,,WRITE", "READ, \t,WRITE",
            "!", "!!READ", "! READ", "!\tALL", "+READ", "READ!", "1",
            "NONE,READ", "READ,NONE", "NONE,NONE", "!NONE", "ALL,NONE",
        )
        for text in invalid:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    solution.parse_flags(text)

    def test_parse_types(self):
        for value in (None, 0, 31, True, 1.0, b"READ", ["READ"], {"READ": 1}):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.parse_flags(value)

    def test_all_masks_and_canonical_format(self):
        names = ("READ", "WRITE", "EXECUTE", "HIDDEN", "ARCHIVE")
        for mask in range(32):
            expected = ",".join(name for index, name in enumerate(names) if mask & (1 << index)) or "NONE"
            with self.subTest(mask=mask):
                self.assertEqual(solution.format_flags(mask), expected)
                self.assertEqual(solution.parse_flags(expected), mask)
        self.assertEqual(solution.parse_flags("ALL"), 31)
        self.assertEqual(solution.format_flags(solution.parse_flags("ARCHIVE,WRITE,READ")), "READ,WRITE,ARCHIVE")

    def test_invalid_masks(self):
        for mask in (-1, -32, -1000, 32, 33, 63, 256, 1 << 100):
            with self.subTest(mask=mask):
                with self.assertRaises(ValueError):
                    solution.format_flags(mask)
        for value in (True, False, None, 1.0, "1", b"1", [], {}):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.format_flags(value)



if __name__ == "__main__":
    unittest.main()
