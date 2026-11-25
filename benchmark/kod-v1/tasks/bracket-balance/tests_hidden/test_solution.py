import unittest

import solution


class BalancedTests(unittest.TestCase):
    def check_cases(self, cases):
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertIs(solution.balanced(text), expected)

    def test_empty_and_ordinary_text(self):
        self.check_cases([(text, True) for text in ('', 'hello', '雪🙂', ' \n\t', '\\', '# plain text')])



    def test_escape_parity(self):
        for quote in ('"', "'"):
            for count in range(9):
                slashes = '\\' * count
                # Even runs leave the next quote free to close the string.
                self.check_cases([
                    (quote + slashes + quote, count % 2 == 0),
                    (quote + slashes + quote + ']' + quote, count % 2 == 1),
                    ('[' + quote + slashes + quote + ']', count % 2 == 0),
                ])

    def test_escaped_characters_and_dangling_escape(self):
        for quote in ('"', "'"):
            for char in ('x', '[', '}', '\n', '雪'):
                self.check_cases([(quote + '\\' + char + quote, True)])
            self.check_cases([
                (quote + '\\' + quote + quote, True),
                (quote + 'abc' + '\\', False),
                (quote + '\\' + quote, False),
                (quote + '\\' * 2, False),
            ])

    def test_backslashes_outside_strings(self):
        self.check_cases([
            ('\\()', True), ('\\[', False), ('\\]', False),
            ('\\"[]"', True), ('\\"', False),
            ('(\\)', True), ('\\' * 4 + "'{}'", True),
        ])

    def test_no_comment_prefix_or_multiline_special_syntax(self):
        self.check_cases([
            ('# [', False), ('# "', False), ('# "["', True),
            ('r"' + '\\' + '"', False),
            ('"""', False), ('""""', True),
            ("''''''", True), ('"a\nb"[]', True),
            ('"a"\n[b]', True),
        ])




if __name__ == '__main__':
    unittest.main()
