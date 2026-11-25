import unittest
from types import MappingProxyType

import solution


class RenderTests(unittest.TestCase):

    def test_substitution_and_repetition(self):
        self.assertEqual(
            solution.render("{{name}}/{{name}}{{_n2}}/{{Name}}", {
                "name": "Ada", "Name": "BOB", "_n2": 12, "unused": "ignored"
            }),
            "Ada/Ada12/BOB",
        )

    def test_value_conversion(self):
        self.assertEqual(
            solution.render("{{a}}|{{b}}|{{c}}|{{d}}", {
                "a": None, "b": False, "c": 0, "d": ""
            }),
            "None|False|0|",
        )

    def test_literal_braces_and_backslashes(self):
        self.assertEqual(solution.render(r"\{\{name\}\}", {}), "{{name}}")
        self.assertEqual(solution.render(r"a\\b\{c\}d", {}), "a\\b{c}d")
        self.assertEqual(solution.render(r"\{{{x}}\}", {"x": "V"}), "{V}")
        self.assertEqual(solution.render(r"\\{{x}}", {"x": "V"}), "\\V")

    def test_insertions_are_not_parsed(self):
        value = "{{missing}}\\q\\{unclosed\n}"
        self.assertEqual(solution.render("A{{x}}B", {"x": value}), "A" + value + "B")

    def test_missing_names(self):
        for template, name, values in (
            ("{{absent}}", "absent", {}),
            ("{{Name}}", "Name", {"name": "x"}),
            ("{{ok}}{{later}}", "later", {"ok": "x"}),
        ):
            with self.subTest(template=template):
                with self.assertRaises(KeyError) as caught:
                    solution.render(template, values)
                self.assertEqual(caught.exception.args, (name,))

    def test_invalid_names(self):
        for name in ("", " name", "name ", "a b", "a-b", "9a", "a.b", "a\nb", "é", "变量", "aé", "a\\b"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    solution.render("{{" + name + "}}", {name: "present"})




    def test_inputs_unchanged_and_read_only_mapping(self):
        values = {"x": "value", "extra": 17}
        before = values.copy()
        template = "{{x}}/{{x}}"
        self.assertEqual(solution.render(template, MappingProxyType(values)), "value/value")
        self.assertEqual(values, before)
        self.assertEqual(template, "{{x}}/{{x}}")


if __name__ == "__main__":
    unittest.main()
