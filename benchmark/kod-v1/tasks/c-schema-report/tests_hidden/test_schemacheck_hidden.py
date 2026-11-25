import unittest

from schemacheck import Issue, counts, format_path, ordered, render, validate


def codes(schema, value):
    return [issue.code for issue in validate(schema, value)]


class HiddenTests(unittest.TestCase):
    def test_type_names_are_strict_about_bool_and_float(self):
        self.assertEqual(validate({"type": "integer"}, True), [Issue((), "type")])
        self.assertEqual(validate({"type": "integer"}, 3.0), [Issue((), "type")])
        self.assertEqual(validate({"type": "integer"}, 3), [])
        self.assertEqual(validate({"type": "number"}, True), [Issue((), "type")])
        self.assertEqual(validate({"type": "number"}, 2.5), [])
        self.assertEqual(validate({"type": "number"}, 2), [])
        self.assertEqual(validate({"type": "boolean"}, 1), [Issue((), "type")])
        self.assertEqual(validate({"type": "boolean"}, False), [])
        self.assertEqual(validate({"type": "null"}, 0), [Issue((), "type")])
        self.assertEqual(validate({"type": "null"}, None), [])
        self.assertEqual(validate({"type": "array"}, (1, 2)), [Issue((), "type")])
        self.assertEqual(validate({"type": "object"}, [("a", 1)]), [Issue((), "type")])
        self.assertEqual(validate({"type": "string"}, b"x"), [Issue((), "type")])
        self.assertEqual(codes({"minimum": 3}, True), [])
        self.assertEqual(codes({"minimum": 3}, 2), ["minimum"])

    def test_enum_requires_same_type_and_value(self):
        schema = {"enum": [1, "a", None, True]}
        for good in (1, "a", None, True):
            self.assertEqual(validate(schema, good), [], msg=repr(good))
        for bad in (1.0, False, 0, "b", "A", [1]):
            self.assertEqual(validate(schema, bad), [Issue((), "enum")], msg=repr(bad))
        self.assertEqual(validate({"type": "string", "enum": ["a"]}, 5), [Issue((), "type")])

    def test_limits_are_inclusive_and_apply_by_value_type(self):
        self.assertEqual(codes({"min_length": 2, "max_length": 3}, "ab"), [])
        self.assertEqual(codes({"min_length": 2, "max_length": 3}, "abc"), [])
        self.assertEqual(codes({"min_length": 2, "max_length": 3}, "a"), ["min_length"])
        self.assertEqual(codes({"min_length": 2, "max_length": 3}, "abcd"), ["max_length"])
        self.assertEqual(codes({"minimum": 5, "maximum": 9}, 5), [])
        self.assertEqual(codes({"minimum": 5, "maximum": 9}, 9), [])
        self.assertEqual(codes({"minimum": 5, "maximum": 9}, 4.999), ["minimum"])
        self.assertEqual(codes({"minimum": 5, "maximum": 9}, 9.5), ["maximum"])
        self.assertEqual(codes({"min_items": 2, "max_items": 3}, [1, 2]), [])
        self.assertEqual(codes({"min_items": 2, "max_items": 3}, [1]), ["min_items"])
        self.assertEqual(codes({"min_items": 2, "max_items": 3}, [1, 2, 3, 4]), ["max_items"])
        self.assertEqual(codes({"min_length": 3, "minimum": 3, "min_items": 3}, 1.5), ["minimum"])
        self.assertEqual(codes({"min_length": 3, "min_items": 3}, {"a": 1}), [])
        self.assertEqual(codes({"min_length": 3, "min_items": 3, "minimum": 9}, None), [])
        self.assertEqual(codes({"min_length": 3, "max_length": 1}, "ab"), ["min_length", "max_length"])
        self.assertEqual(codes({"enum": ["xyz"], "min_length": 3}, "ab"), ["enum", "min_length"])

    def test_object_issue_order_required_properties_unexpected(self):
        schema = {
            "required": ["z", "a"],
            "properties": {"m": {"type": "integer"}, "b": {"type": "integer"}},
            "additional": False,
        }
        value = {"q": 1, "m": "s", "b": "t", "p": 0}
        self.assertEqual(validate(schema, value), [
            Issue(("z",), "required"),
            Issue(("a",), "required"),
            Issue(("m",), "type"),
            Issue(("b",), "type"),
            Issue(("p",), "unexpected"),
            Issue(("q",), "unexpected"),
        ])
        self.assertEqual(validate({"properties": {"m": {"type": "integer"}}}, {"x": 1, "y": 2}), [])
        self.assertEqual(validate({"required": ["k"], "properties": {"k": {"type": "integer"}}}, {}),
                         [Issue(("k",), "required")])

    def test_array_issue_order_and_nested_paths(self):
        schema = {"type": "array", "max_items": 2, "items": {"type": "integer"}}
        self.assertEqual(validate(schema, [1, "x", 2.5]), [
            Issue((), "max_items"), Issue((1,), "type"), Issue((2,), "type")])
        nested = {"type": "object", "properties": {"rows": {"type": "array", "items": {
            "type": "object", "required": ["id"], "properties": {"id": {"type": "integer"}}}}}}
        self.assertEqual(validate(nested, {"rows": [{"id": 1}, {}, {"id": "x"}]}), [
            Issue(("rows", 1, "id"), "required"), Issue(("rows", 2, "id"), "type")])

    def test_type_failure_stops_all_other_checks_for_that_value(self):
        schema = {"type": "string", "enum": ["a"], "min_length": 5, "minimum": 3}
        self.assertEqual(validate(schema, 7), [Issue((), "type")])
        schema = {"type": "object", "required": ["a"], "additional": False}
        self.assertEqual(validate(schema, [1]), [Issue((), "type")])

    def test_report_orders_indices_numerically(self):
        issues = validate({"items": {"type": "string"}}, list(range(12)))
        expected = "".join("$[%d]: type\n" % number for number in range(12)) + "-- 12 issues\n"
        self.assertEqual(render(issues), expected)

    def test_report_sort_order_of_mixed_paths(self):
        shuffled = [
            Issue(("a", "b"), "y"), Issue((10,), "x"), Issue(("a",), "z"), Issue(("a",), "b"),
            Issue((5,), "x"), Issue((), "type"), Issue(("a", 0), "x"), Issue((0,), "x"),
        ]
        self.assertEqual(ordered(shuffled), [
            Issue((), "type"), Issue((0,), "x"), Issue((5,), "x"), Issue((10,), "x"),
            Issue(("a",), "b"), Issue(("a",), "z"), Issue(("a", 0), "x"), Issue(("a", "b"), "y"),
        ])
        self.assertEqual(render(shuffled),
                         "$: type\n$[0]: x\n$[5]: x\n$[10]: x\n$.a: b\n$.a: z\n$.a[0]: x\n$.a.b: y\n-- 8 issues\n")
        self.assertEqual(format_path(("a", 2, "b c", 0)), "$.a[2].b c[0]")
        self.assertEqual(format_path(()), "$")

    def test_duplicates_are_reported_once_and_paths_may_be_lists(self):
        issues = [Issue(("a",), "x"), Issue(["a"], "x"), Issue(("a",), "x"), Issue(("a",), "y")]
        self.assertEqual(ordered(issues), [Issue(("a",), "x"), Issue(("a",), "y")])
        self.assertEqual(counts(issues), {"x": 1, "y": 1})
        self.assertEqual(render(issues[:3]), "$.a: x\n-- 1 issue\n")
        self.assertEqual(counts([Issue((1,), "z"), Issue((2,), "z"), Issue((), "a")]), {"a": 1, "z": 2})
        self.assertEqual(list(counts([Issue((), "z"), Issue((), "a")])), ["a", "z"])
        self.assertEqual(issues[1].path, ["a"])

    def test_schema_errors(self):
        with self.assertRaises(TypeError):
            validate("object", {})
        with self.assertRaises(TypeError):
            validate({"properties": {"a": 5}}, {"a": 1})
        with self.assertRaises(TypeError):
            validate({"items": [{"type": "integer"}]}, [1])
        with self.assertRaises(ValueError):
            validate({"type": "integr"}, 1)
        with self.assertRaises(ValueError):
            validate({"type": ["string"]}, "x")
        self.assertEqual(validate({"properties": {"a": 5}}, {}), [])
        self.assertEqual(validate({"properties": {"a": {"type": "bogus"}}}, {}), [])
        with self.assertRaises(ValueError):
            validate({"properties": {"a": {"type": "bogus"}}}, {"a": 1})
        self.assertEqual(validate({"items": 5}, []), [])


if __name__ == "__main__":
    unittest.main()
