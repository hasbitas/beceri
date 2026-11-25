import unittest

import confl
from confl import ConfigError, Token, parse, tokenize
from confl.errors import ConfigError as ErrorsConfigError


def failure(text, func=parse):
    try:
        func(text)
    except ConfigError as exc:
        return (exc.line, exc.column)
    raise AssertionError("ConfigError not raised for %r" % (text,))


class HiddenConfigTests(unittest.TestCase):
    def test_exports_and_error_type(self):
        self.assertIs(confl.ConfigError, ErrorsConfigError)
        self.assertTrue(issubclass(ConfigError, ValueError))
        with self.assertRaises(ConfigError) as caught:
            parse("= 1")
        self.assertIsInstance(caught.exception.message, str)
        self.assertEqual((caught.exception.line, caught.exception.column), (1, 1))

    def test_token_stream_layout(self):
        text = "[a.b]\t# note\r\nk-1 = [1, \"x\"] # tail\n  \n"
        self.assertEqual(
            tokenize(text),
            [
                Token("LBRACKET", "[", 1, 1),
                Token("NAME", "a", 1, 2),
                Token("DOT", ".", 1, 3),
                Token("NAME", "b", 1, 4),
                Token("RBRACKET", "]", 1, 5),
                Token("NEWLINE", "\n", 1, 14),
                Token("NAME", "k-1", 2, 1),
                Token("EQUALS", "=", 2, 5),
                Token("LBRACKET", "[", 2, 7),
                Token("INT", 1, 2, 8),
                Token("COMMA", ",", 2, 9),
                Token("STRING", "x", 2, 11),
                Token("RBRACKET", "]", 2, 14),
                Token("NEWLINE", "\n", 2, 22),
                Token("NEWLINE", "\n", 3, 3),
                Token("EOF", "", 4, 1),
            ],
        )
        self.assertEqual(tokenize(""), [Token("EOF", "", 1, 1)])
        self.assertEqual(tokenize("# only"), [Token("EOF", "", 1, 7)])

    def test_ints_and_names(self):
        tokens = tokenize("-12 007 -0 _x9-y 12ab")
        self.assertEqual(
            [(t.kind, t.value, t.column) for t in tokens],
            [("INT", -12, 1), ("INT", 7, 5), ("INT", 0, 9), ("NAME", "_x9-y", 12),
             ("INT", 12, 18), ("NAME", "ab", 20), ("EOF", "", 22)],
        )

    def test_string_decoding_and_columns(self):
        self.assertEqual(tokenize('"a#b" "é中"')[0], Token("STRING", "a#b", 1, 1))
        tokens = tokenize('"x\\ty" , "\\\\" "\\"" "\\\\\\"" 5')
        self.assertEqual(
            [(t.kind, t.value, t.column) for t in tokens],
            [("STRING", "x\ty", 1), ("COMMA", ",", 8), ("STRING", "\\", 10),
             ("STRING", '"', 15), ("STRING", '\\"', 20), ("INT", 5, 27), ("EOF", "", 28)],
        )
        self.assertEqual(tokenize('""')[0], Token("STRING", "", 1, 1))
        self.assertEqual(parse('s = "end\\\\"\nt = "x"'), {"s": "end\\", "t": "x"})

    def test_tokenizer_errors(self):
        self.assertEqual(failure('a = "abc', tokenize), (1, 5))
        self.assertEqual(failure('\n\n  "abc\nd"', tokenize), (3, 3))
        self.assertEqual(failure('a = "x\\q"', tokenize), (1, 7))
        self.assertEqual(failure('a = "xy\\', tokenize), (1, 8))
        self.assertEqual(failure('a = "x\\ty\\z"', tokenize), (1, 10))
        self.assertEqual(failure('a = "x\\ty" @', tokenize), (1, 12))
        self.assertEqual(failure('a = "\\n\\n\\n" -', tokenize), (1, 14))
        self.assertEqual(failure("a = 'x'", tokenize), (1, 5))
        self.assertEqual(failure("a = 1\n  b = +2", tokenize), (2, 7))
        self.assertEqual(failure("k = {", tokenize), (1, 5))
        self.assertEqual(failure("café = 1", tokenize), (1, 4))
        self.assertEqual(failure("a = 1\r\nb = $", tokenize), (2, 5))

    def test_nested_documents(self):
        text = (
            "top = 1\n"
            "[a.b.c]\n"
            "x = [1, [2, 3], [], \"s\", true,]\n"
            "y = [\n"
            "  1,\n"
            "  2, # two\n"
            "  false\n"
            "]\n"
            "[a]\n"
            "z = \"\"\n"
            "[d]\n"
        )
        self.assertEqual(
            parse(text),
            {
                "top": 1,
                "a": {"b": {"c": {"x": [1, [2, 3], [], "s", True], "y": [1, 2, False]}}, "z": ""},
                "d": {},
            },
        )
        self.assertEqual(parse(""), {})
        self.assertEqual(parse("\n# c\n\n   \n"), {})
        self.assertEqual(parse("a=1\r\nb=2"), {"a": 1, "b": 2})
        self.assertEqual(parse("a = true\nb = false\nc = []"), {"a": True, "b": False, "c": []})
        self.assertEqual(parse("true = 1")["true"], 1)

    def test_section_rules(self):
        self.assertEqual(parse("[a.b]\n[a]\nx = 1"), {"a": {"b": {}, "x": 1}})
        self.assertEqual(parse("[a]\n[a.b]\n[c]\n[c.d]"), {"a": {"b": {}}, "c": {"d": {}}})
        self.assertEqual(failure("[a]\n[a]\n"), (2, 1))
        self.assertEqual(failure("[a]\nx = 1\n[b]\n\n  [a]"), (5, 3))
        self.assertEqual(failure("[a.b]\nx = 1\n[a.b]\n"), (3, 1))
        self.assertEqual(failure("[a]\n[a.b]\n[a]\n"), (3, 1))
        self.assertEqual(failure("a = 1\n[a]\n"), (2, 1))
        self.assertEqual(failure("[a]\nb = 1\n[a.b]\n"), (3, 1))
        self.assertEqual(failure("a = [1]\n[x]\n[a.b.c]"), (3, 1))
        self.assertEqual(failure("[a.b]\nc = 1\n[a]\nb = 2\n"), (4, 1))

    def test_syntax_error_positions(self):
        cases = [
            ("a 1", (1, 3)),
            ("a =", (1, 4)),
            ("a = \nb = 1", (1, 5)),
            ("a = 1 2", (1, 7)),
            ("a = 1 = 2", (1, 7)),
            ("a = [1] ]", (1, 9)),
            ("a = [1,, 2]", (1, 8)),
            ("a = [,]", (1, 6)),
            ("a = [1 2]", (1, 8)),
            ("a = [1,\n2", (2, 2)),
            ("a = [", (1, 6)),
            ("a = [1", (1, 7)),
            ("a = ]", (1, 5)),
            ("a = maybe", (1, 5)),
            ("a = True", (1, 5)),
            ("a = 1.5", (1, 6)),
            ("a.b = 1", (1, 2)),
            ("[]", (1, 2)),
            ("[a.]", (1, 4)),
            ("[a b]", (1, 4)),
            ("[a", (1, 3)),
            ("[a] x", (1, 5)),
            ("[a]\n[b\n", (2, 3)),
            ("\n\n  5 = 1", (3, 3)),
            (",", (1, 1)),
            ('"k" = 1', (1, 1)),
            ("a = 1\n\n  b", (3, 4)),
        ]
        for text, position in cases:
            with self.subTest(text=text):
                self.assertEqual(failure(text), position)

    def test_errors_after_escaped_strings_keep_columns(self):
        self.assertEqual(failure('a = "x\\ty" 5'), (1, 12))
        self.assertEqual(failure('a = ["\\\\", "\\n" 3]'), (1, 17))

    def test_non_string_input(self):
        for value in (None, 5, b"a = 1", ["a = 1"]):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    parse(value)
                with self.assertRaises(TypeError):
                    tokenize(value)
        result = parse("a = [1]")
        self.assertIsNot(result, parse("a = [1]"))


if __name__ == "__main__":
    unittest.main()
