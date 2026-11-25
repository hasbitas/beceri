import unittest

import solution


class FlagTests(unittest.TestCase):
    def test_empty_and_none(self):
        for text in ("", " \t\n", "NONE", " \u2003NONE\t"):
            with self.subTest(text=text):
                self.assertEqual(solution.parse_flags(text), 0)

    def test_individual_flags_and_duplicates(self):
        for name, bit in (("READ", 1), ("WRITE", 2), ("EXECUTE", 4), ("HIDDEN", 8), ("ARCHIVE", 16)):
            with self.subTest(name=name):
                self.assertEqual(solution.parse_flags(name), bit)
                self.assertEqual(solution.parse_flags(name + "," + name), bit)
                self.assertEqual(solution.parse_flags("!" + name), 0)
        self.assertEqual(solution.parse_flags(" ARCHIVE ,\tREAD, EXECUTE\n"), 21)






    def test_calls_do_not_share_state_or_print(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO

        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(solution.parse_flags("ALL"), 31)
            self.assertEqual(solution.parse_flags("!READ"), 0)
            self.assertEqual(solution.format_flags(1), "READ")
            self.assertEqual(solution.parse_flags("WRITE"), 2)
            self.assertEqual(solution.format_flags(0), "NONE")
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
