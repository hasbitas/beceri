import unittest

from resolver import ConflictError, format_version, generate_lock, newest, parse_lock, parse_version, render_lock, resolve

REGISTRY = {
    "app-core": {"1.0.0": {"net": 1}, "1.2.0": {"net": 2, "util": 1}},
    "net": {"1.4.0": {}, "2.0.1": {"util": 1}, "2.1.0": {"util": 1}},
    "util": {"1.0.0": {}, "1.3.5": {}, "2.0.0": {}},
}


class VisibleTests(unittest.TestCase):
    def test_resolves_newest_matching_major_transitively(self):
        self.assertEqual(resolve(REGISTRY, {"app-core": 1}),
                         {"app-core": "1.2.0", "net": "2.1.0", "util": "1.3.5"})

    def test_lock_text_is_sorted_and_round_trips(self):
        resolution = resolve(REGISTRY, {"net": 2, "app-core": 1})
        text = render_lock(REGISTRY, resolution)
        self.assertEqual(text, "# lock v1\n"
                               "app-core==1.2.0 requires net@2,util@1\n"
                               "net==2.1.0 requires util@1\n"
                               "util==1.3.5\n")
        self.assertEqual(parse_lock(text), {
            "app-core": ("1.2.0", {"net": 2, "util": 1}),
            "net": ("2.1.0", {"util": 1}),
            "util": ("1.3.5", {}),
        })
        self.assertEqual(generate_lock(REGISTRY, {"net": 2, "app-core": 1}), text)

    def test_different_majors_for_one_package_conflict(self):
        with self.assertRaises(ConflictError):
            resolve(REGISTRY, {"app-core": 1, "net": 1})

    def test_version_helpers(self):
        self.assertEqual(parse_version("3.0.12"), (3, 0, 12))
        self.assertEqual(format_version((4, 5, 6)), "4.5.6")
        self.assertEqual(newest(["1.0.0", "1.2.0", "2.0.0"], 1), "1.2.0")
        self.assertIsNone(newest(["1.0.0"], 3))


if __name__ == "__main__":
    unittest.main()
