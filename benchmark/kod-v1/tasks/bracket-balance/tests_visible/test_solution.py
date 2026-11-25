import unittest

import solution


class BalancedTests(unittest.TestCase):
    def check_cases(self, cases):
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertIs(solution.balanced(text), expected)


    def test_bracket_order(self):
        self.check_cases([
            ('()[]{}', True), ('{[()]}', True), ('([{}])([])', True),
            ('([)]', False), ('{(})', False), (')(', False),
            ('(', False), ('[[]', False), ('{}]', False),
        ])
        for char in '()[]{}':
            self.check_cases([(char, False)])

    def test_quoted_brackets_and_other_quote(self):
        for quote, other in [('"', "'"), ("'", '"')]:
            self.check_cases([
                (quote + ')]}{[(' + quote, True),
                ('[' + quote + other + ']' + other + quote + ']', True),
                (quote + '\n雪' + quote, True),
                ('(' + quote + ')' + quote, False),
                (quote + 'text', False),
            ])





    def test_adjacent_strings_and_nesting(self):
        self.check_cases([
            ('["}"\'("\']', True),
            ('"["\']\'{}', True),
            ('"ok"([)]', False),
            ('[]"unterminated', False),
        ])
        nested = '([{' * 4000 + '"[}]"' + '}])' * 4000
        self.assertIs(solution.balanced(nested), True)
        self.assertIs(solution.balanced(nested + '('), False)

    def test_non_string_inputs(self):
        for value in (None, True, 0, 1.5, b'()', [], {}, ('(', ')')):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.balanced(value)


if __name__ == '__main__':
    unittest.main()
