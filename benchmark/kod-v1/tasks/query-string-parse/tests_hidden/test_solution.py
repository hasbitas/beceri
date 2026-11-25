import unittest

import solution


class ParseQueryTests(unittest.TestCase):
    def test_empty_queries_and_fields(self):
        for qs in ("", "?", "&", "&&&", "?&&"):
            with self.subTest(qs=qs):
                self.assertEqual(solution.parse_query(qs), {})
        self.assertEqual(solution.parse_query("&&a=1&&b=2&"),
                         {"a": ["1"], "b": ["2"]})



    def test_decoded_delimiters_are_data(self):
        self.assertEqual(solution.parse_query("a%26b=x%26y&k%3Dv=p%3Dq&%26=%3d"),
                         {"a&b": ["x&y"], "k=v": ["p=q"], "&": ["="]})
        self.assertEqual(solution.parse_query("%26&%3D&x=%26%26"),
                         {"&": [""], "=": [""], "x": ["&&"]})

    def test_plus_and_exactly_one_decoding_pass(self):
        self.assertEqual(solution.parse_query("a+b=c+d&x=%2B+%2520&%2526=%253D"),
                         {"a b": ["c d"], "x": ["+ %20"], "%26": ["%3D"]})

    def test_repeated_decoded_keys_and_iteration_order(self):
        result = solution.parse_query("z=0&b=1&%62=2&a+b=3&a%20b=4&z=5&b=6")
        self.assertEqual(result, {"z": ["0", "5"], "b": ["1", "2", "6"],
                                  "a b": ["3", "4"]})
        self.assertEqual(list(result), ["z", "b", "a b"])

    def test_utf8_and_literal_unicode(self):
        self.assertEqual(solution.parse_query("%E2%98%83=caf%C3%A9&雪=山&%e9%9b%aa=水"),
                         {"☃": ["café"], "雪": ["山", "水"]})



    def test_whitespace_hash_and_semicolon_are_preserved(self):
        self.assertEqual(solution.parse_query(" a = b ;c#d&x=1;z=2#frag&k\t=\n"),
                         {" a ": [" b ;c#d"], "x": ["1;z=2#frag"], "k\t": ["\n"]})
        self.assertEqual(solution.parse_query("a=%00&%00=%00"),
                         {"a": ["\x00"], "\x00": ["\x00"]})


    def test_results_are_independent(self):
        first = solution.parse_query("a=1&a=2")
        second = solution.parse_query("a=1&a=2")
        self.assertIsNot(first, second)
        self.assertIsNot(first["a"], second["a"])
        first["a"].append("changed")
        first["extra"] = ["value"]
        self.assertEqual(second, {"a": ["1", "2"]})
        self.assertEqual(solution.parse_query(""), {})


if __name__ == "__main__":
    unittest.main()
