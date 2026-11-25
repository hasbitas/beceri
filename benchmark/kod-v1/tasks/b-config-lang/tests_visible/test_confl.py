import unittest

from confl import ConfigError, Token, parse, tokenize


class VisibleConfigTests(unittest.TestCase):
    def test_document_with_sections(self):
        text = (
            "# service settings\n"
            "name = \"demo\"\n"
            "retries = 3\n"
            "\n"
            "[server]\n"
            "debug = true\n"
            "hosts = [\"a\", \"b\"]\n"
            "\n"
            "[server.limits]\n"
            "max-size = -10\n"
        )
        self.assertEqual(
            parse(text),
            {
                "name": "demo",
                "retries": 3,
                "server": {
                    "debug": True,
                    "hosts": ["a", "b"],
                    "limits": {"max-size": -10},
                },
            },
        )

    def test_tokens_have_positions(self):
        self.assertEqual(
            tokenize("a = 1\n"),
            [
                Token("NAME", "a", 1, 1),
                Token("EQUALS", "=", 1, 3),
                Token("INT", 1, 1, 5),
                Token("NEWLINE", "\n", 1, 6),
                Token("EOF", "", 2, 1),
            ],
        )

    def test_string_escapes(self):
        self.assertEqual(parse('path = "C:\\\\temp\\\\"\n'), {"path": "C:\\temp\\"})
        self.assertEqual(parse('s = "a\\tb\\"c\\n"'), {"s": 'a\tb"c\n'})

    def test_error_positions(self):
        with self.assertRaises(ConfigError) as caught:
            parse("a = 1\nb = maybe\n")
        self.assertEqual((caught.exception.line, caught.exception.column), (2, 5))
        with self.assertRaises(ConfigError) as caught:
            parse("a = 1\na = 2\n")
        self.assertEqual((caught.exception.line, caught.exception.column), (2, 1))
        with self.assertRaises(TypeError):
            parse(None)


if __name__ == "__main__":
    unittest.main()
