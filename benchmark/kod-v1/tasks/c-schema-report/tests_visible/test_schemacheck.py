import unittest

from schemacheck import Issue, counts, render, validate

SCHEMA = {
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "min_length": 2},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}


class VisibleTests(unittest.TestCase):
    def test_issues_in_discovery_order(self):
        value = {"id": 0, "tags": ["ok", 5]}
        self.assertEqual(validate(SCHEMA, value), [
            Issue(("name",), "required"),
            Issue(("id",), "minimum"),
            Issue(("tags", 1), "type"),
        ])

    def test_valid_value_and_ok_report(self):
        value = {"id": 7, "name": "Zoe", "tags": []}
        self.assertEqual(validate(SCHEMA, value), [])
        self.assertEqual(render([]), "ok\n")

    def test_report_and_counts(self):
        issues = validate(SCHEMA, {"id": 0, "tags": ["ok", 5]})
        self.assertEqual(render(issues), "$.id: minimum\n$.name: required\n$.tags[1]: type\n-- 3 issues\n")
        self.assertEqual(counts(issues), {"minimum": 1, "required": 1, "type": 1})


if __name__ == "__main__":
    unittest.main()
