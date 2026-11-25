import unittest

from resolver import (ConflictError, ResolutionError, format_version, generate_lock, newest, parse_lock,
                      parse_version, render_lock, resolve)


class HiddenTests(unittest.TestCase):
    def test_versions_compare_numerically(self):
        self.assertEqual(newest(["1.9.2", "1.10.0", "1.2.40"], 1), "1.10.0")
        self.assertEqual(newest({"3.0.9": {}, "3.0.10": {}}, 3), "3.0.10")
        self.assertEqual(newest([], 1), None)

    def test_version_validation(self):
        for bad in ("1.2", "1.2.3.4", "01.2.3", "1.2.x", " 1.2.3", "1.2.3\n", "-1.0.0", "1.0.0-rc1", "", "١.0.0"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                parse_version(bad)
        with self.assertRaises(TypeError):
            parse_version(1.5)
        with self.assertRaises(ValueError):
            format_version((1, 2))
        with self.assertRaises(ValueError):
            newest(["1.0.0", "bogus"], 1)

    def test_conflicting_majors_are_reported(self):
        registry = {
            "a": {"1.0.0": {"c": 1}},
            "b": {"1.0.0": {"c": 2}},
            "c": {"1.0.0": {}, "2.0.0": {}},
        }
        with self.assertRaises(ConflictError):
            resolve(registry, {"a": 1, "b": 1})
        with self.assertRaises(ConflictError):
            resolve(registry, {"a": 1, "c": 2})
        self.assertTrue(issubclass(ConflictError, ResolutionError))
        self.assertEqual(resolve(registry, {"a": 1, "c": 1}), {"a": "1.0.0", "c": "1.0.0"})

    def test_missing_package_or_major(self):
        registry = {"a": {"1.0.0": {"ghost": 1}}, "b": {"1.0.0": {}}}
        with self.assertRaises(ResolutionError):
            resolve(registry, {"a": 1})
        with self.assertRaises(ResolutionError):
            resolve(registry, {"b": 2})
        with self.assertRaises(ResolutionError):
            resolve(registry, {"nope": 1})
        self.assertNotIsInstance(ResolutionError("x"), ConflictError)

    def test_only_newest_versions_dependencies_count(self):
        registry = {
            "a": {"1.0.0": {"old-dep": 9}, "1.1.0": {}},
            "old-dep": {"9.0.0": {}},
        }
        self.assertEqual(resolve(registry, {"a": 1}), {"a": "1.1.0"})

    def test_cycles_and_shared_dependencies(self):
        registry = {
            "a": {"1.0.0": {"b": 1, "d": 1}},
            "b": {"1.0.0": {"a": 1, "d": 1}},
            "d": {"1.0.0": {}, "1.0.1": {}},
        }
        self.assertEqual(resolve(registry, {"b": 1}), {"a": "1.0.0", "b": "1.0.0", "d": "1.0.1"})
        self.assertEqual(list(resolve(registry, {"d": 1, "b": 1})), ["a", "b", "d"])
        self.assertEqual(resolve(registry, {}), {})

    def test_requirement_validation(self):
        registry = {"a": {"1.0.0": {"b": -1}}, "b": {"1.0.0": {}}}
        with self.assertRaises(TypeError):
            resolve(registry, {"a": "1"})
        with self.assertRaises(TypeError):
            resolve(registry, {"a": True})
        with self.assertRaises(ValueError):
            resolve(registry, {"a": -1})
        with self.assertRaises(ValueError):
            resolve(registry, {"a": 1})
        with self.assertRaises(ValueError):
            resolve({"a": {"1.x.0": {}}}, {"a": 1})

    def test_render_sorts_names_and_dependencies(self):
        registry = {
            "zed": {"1.0.0": {"mid": 3, "alpha": 10}},
            "alpha": {"10.0.0": {}},
            "mid": {"3.1.4": {}},
        }
        resolution = {"zed": "1.0.0", "mid": "3.1.4", "alpha": "10.0.0"}
        self.assertEqual(render_lock(registry, resolution),
                         "# lock v1\nalpha==10.0.0\nmid==3.1.4\nzed==1.0.0 requires alpha@10,mid@3\n")
        self.assertEqual(render_lock(registry, {}), "# lock v1\n")
        with self.assertRaises(KeyError):
            render_lock(registry, {"zed": "9.9.9"})

    def test_generate_lock_end_to_end(self):
        registry = {
            "web": {"2.0.0": {"http": 1, "log": 4}, "2.3.0": {"http": 1, "log": 4}},
            "http": {"1.9.0": {"log": 4}, "1.10.0": {"log": 4}},
            "log": {"4.0.0": {}, "4.0.2": {}, "5.0.0": {}},
        }
        self.assertEqual(generate_lock(registry, {"web": 2}),
                         "# lock v1\nhttp==1.10.0 requires log@4\nlog==4.0.2\nweb==2.3.0 requires http@1,log@4\n")

    def test_parse_lock_accepts_comments_and_blank_lines(self):
        text = "# lock v1\n\n# generated\nb==1.0.0 requires a@0\na==0.10.0\n\n"
        self.assertEqual(parse_lock(text), {"b": ("1.0.0", {"a": 0}), "a": ("0.10.0", {})})
        self.assertEqual(parse_lock("# lock v1"), {})

    def test_parse_lock_is_looser_than_the_canonical_text(self):
        self.assertEqual(parse_lock("# lock v1\n"), {})
        self.assertEqual(parse_lock("# lock v1\nb==2.0.0"), {"b": ("2.0.0", {})})
        self.assertEqual(parse_lock("# lock v1\nz==1.0.0 requires y@2,a@1\ny==2.0.0\na==1.0.0\n"),
                         {"z": ("1.0.0", {"y": 2, "a": 1}), "y": ("2.0.0", {}), "a": ("1.0.0", {})})

    def test_parse_lock_rejects_malformed_text(self):
        bad_texts = [
            "",
            "# lock v2\na==1.0.0\n",
            "a==1.0.0\n",
            "# lock v1\na==1.0.0\na==1.0.1\n",
            "# lock v1\na==1.0\n",
            "# lock v1\na==01.0.0\n",
            "# lock v1\nA==1.0.0\n",
            "# lock v1\na == 1.0.0\n",
            "# lock v1\na==1.0.0 \n",
            "# lock v1\na==1.0.0 requires \n",
            "# lock v1\na==1.0.0 requires b@1,b@2\n",
            "# lock v1\na==1.0.0 requires b@01\n",
            "# lock v1\na==1.0.0 requires b\n",
            "# lock v1\r\na==1.0.0\r\n",
            "# lock v1\n# comment\r\n",
            "# lock v1\na==1.0.0\n#\r\n",
            "# lock v1\n\ra==1.0.0\n",
            "# lock v1\na==1.0.0\n# trailing\r",
        ]
        for text in bad_texts:
            with self.assertRaises(ValueError, msg=repr(text)):
                parse_lock(text)
        with self.assertRaises(TypeError):
            parse_lock(None)


if __name__ == "__main__":
    unittest.main()
