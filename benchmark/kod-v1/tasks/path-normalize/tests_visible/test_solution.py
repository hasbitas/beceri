import unittest

import solution


class NormalizeTests(unittest.TestCase):
    def check_cases(self, cases):
        for path, expected in cases:
            with self.subTest(path=repr(path)):
                actual = solution.normalize(path)
                self.assertIsInstance(actual, str)
                self.assertEqual(actual, expected)

    def test_empty_and_current_directory(self):
        self.check_cases([
            ('', '.'), ('.', '.'), ('./', './'), ('././', './'),
            ('./.', '.'), ('a/..', '.'), ('a/../', './'),
            ('a/../.', '.'), ('a/.././', './'),
        ])

    def test_absolute_roots(self):
        self.check_cases([
            ('/', '/'), ('//', '/'), ('////', '/'), ('/.', '/'),
            ('/..', '/'), ('/../../', '/'), ('//a', '/a'),
            ('///a/../..', '/'), ('/a/../../../b/', '/b/'),
        ])




    def test_trailing_slashes(self):
        self.check_cases([
            ('a/', 'a/'), ('a////', 'a/'), ('/a///', '/a/'),
            ('../', '../'), ('../../', '../../'),
            ('a/../../', '../'), ('a/b/../../', './'),
            ('/a/b/../../', '/'), ('a/b/..', 'a'), ('a/b/../', 'a/'),
        ])

    def test_components_are_literal(self):
        self.check_cases([
            ('.../..hidden/./x..', '.../..hidden/x..'),
            ('.../../x', 'x'), (' . / .. /x ', ' . / .. /x '),
            ('a\\b/../c', 'c'), ('a\\..\\b', 'a\\..\\b'),
            ('~/x/$HOME', '~/x/$HOME'), ('a\x00b/./c', 'a\x00b/c'),
            ('café/δ/../β', 'café/β'),
            ('a\nb/./c\t', 'a\nb/c\t'),
        ])





if __name__ == '__main__':
    unittest.main()
