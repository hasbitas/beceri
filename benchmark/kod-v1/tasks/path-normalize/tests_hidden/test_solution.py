import unittest

import solution


class NormalizeTests(unittest.TestCase):
    def check_cases(self, cases):
        for path, expected in cases:
            with self.subTest(path=repr(path)):
                actual = solution.normalize(path)
                self.assertIsInstance(actual, str)
                self.assertEqual(actual, expected)



    def test_separator_and_dot_collapse(self):
        self.check_cases([
            ('a//b///c', 'a/b/c'), ('a/./b/./c', 'a/b/c'),
            ('./a//./b///', 'a/b/'), ('//a//./b///', '/a/b/'),
            ('a/.', 'a'), ('/a/.', '/a'),
        ])

    def test_ordinary_parent_cancellation(self):
        self.check_cases([
            ('a/b/../c', 'a/c'), ('a/b/../../c', 'c'),
            ('/a/b/../../c', '/c'), ('a/../b/../c/..', '.'),
            ('a/b/c/../../d/../e/', 'a/e/'),
        ])

    def test_unresolved_relative_parents(self):
        self.check_cases([
            ('..', '..'), ('../..', '../..'), ('../../..', '../../..'),
            ('../../a', '../../a'), ('../a/..', '..'),
            ('../a/../..', '../..'), ('a/../../b', '../b'),
            ('a/../../../b', '../../b'),
            ('../../a/b/../../../c', '../../../c'),
            ('.././../x/../../', '../../../'),
        ])



    def test_wrong_types(self):
        for value in (None, 0, 1.5, True, b'a/b', [], {}, ('a',)):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    solution.normalize(value)

    def test_long_cancellation_and_parent_runs(self):
        depth = 400
        self.check_cases([
            ('x/' * depth + '../' * depth, './'),
            ('/' + 'x/' * depth + '../' * (depth + 10), '/'),
            ('../' * depth + 'x/../', '../' * depth),
            ('x/' * depth + '../' * (depth + 3), '../../../'),
        ])

    def test_normalized_results_are_stable(self):
        paths = (
            '', '.', './', '/', '//a//b/', 'a/./b/../../',
            '../../x/../y/', 'a/../../../b', '/../../c/..',
            '.../x/../', 'a\\b/./',
        )
        for path in paths:
            with self.subTest(path=path):
                normalized = solution.normalize(path)
                self.assertEqual(solution.normalize(normalized), normalized)


if __name__ == '__main__':
    unittest.main()
