import unittest

import solution


class ParseQueryTests(unittest.TestCase):

    def test_missing_values_empty_keys_and_first_equals(self):
        self.assertEqual(solution.parse_query("flag&x=&=v&=&a=b=c&flag"),
                         {"flag": ["", ""], "x": [""],
                          "": ["v", ""], "a": ["b=c"]})

    def test_leading_question_mark_removed_once(self):
        self.assertEqual(solution.parse_query("??a=1&?b=2"),
                         {"?a": ["1"], "?b": ["2"]})
        self.assertEqual(solution.parse_query("%3Fa=1"), {"?a": ["1"]})





    def test_invalid_utf8_replacement(self):
        self.assertEqual(solution.parse_query("%FF=%C3%28&x=%E2%82&x=%80%81"),
                         {"\ufffd": ["\ufffd("], "x": ["\ufffd", "\ufffd\ufffd"]})

    def test_malformed_escapes_remain_literal(self):
        self.assertEqual(solution.parse_query("%=x%&%G1=%2&x=%GG%41%4Z&y=%%41"),
                         {"%": ["x%"], "%G1": ["%2"],
                          "x": ["%GGA%4Z"], "y": ["%A"]})


    def test_non_string_inputs(self):
        for value in (None, b"a=1", 1, False, [], {}, ("a",)):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    solution.parse_query(value)



if __name__ == "__main__":
    unittest.main()
