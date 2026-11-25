import unittest
from types import MappingProxyType

import solution


class RenderTests(unittest.TestCase):
    def test_empty_and_plain_text(self):
        for text in ("", "plain text", "héllo 世界\n\tend"):
            with self.subTest(text=text):
                self.assertEqual(solution.render(text, {}), text)







    def test_invalid_delimiters(self):
        for template in ("{", "}", "{{", "}}", "x{y", "x}y", "{{x}", "{{x", "{{{x}}}", "{{a{{b}}}}", "{{x}}}", "{{x}}{"):
            with self.subTest(template=template):
                with self.assertRaises(ValueError):
                    solution.render(template, {"x": "X", "a": "A", "b": "B"})

    def test_invalid_escapes(self):
        for template in ("\\", "end\\", r"\q", r"\n", r"\ ", "\\\n", r"\{x}"):
            with self.subTest(template=template):
                with self.assertRaises(ValueError):
                    solution.render(template, {})

    def test_left_to_right_errors(self):
        for template in ("{{missing}}{", "{{missing}}\\q", "{{missing}}{{ bad }}"):
            with self.subTest(template=template):
                with self.assertRaises(KeyError) as caught:
                    solution.render(template, {})
                self.assertEqual(caught.exception.args, ("missing",))
        for template in ("\\q{{missing}}", "{{ bad }}{{missing}}", "{{a{{missing}}"):
            with self.subTest(template=template):
                with self.assertRaises(ValueError):
                    solution.render(template, {})



if __name__ == "__main__":
    unittest.main()
