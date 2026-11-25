import unittest

import solution


class DictSubclass(dict):
    pass


class SolutionTests(unittest.TestCase):


    def test_empty_leaves_are_retained_and_copied(self):
        empty = DictSubclass()
        source = {'a': {'b': empty}, 'c': empty}
        flat = solution.flatten(source)
        self.assertEqual(flat, {'a.b': {}, 'c': {}})
        self.assertIsNot(flat['a.b'], empty)
        self.assertIsNot(flat['a.b'], flat['c'])
        nested = solution.unflatten(flat)
        self.assertEqual(nested, source)
        self.assertIsNot(nested['a']['b'], flat['a.b'])
        self.assertIsNot(nested['a']['b'], nested['c'])
        self.assertIs(type(nested['a']['b']), dict)
        self.assertEqual(source, {'a': {'b': {}}, 'c': {}})

    def test_leaf_identity_and_no_inspection(self):
        leaves = [[{'bad.key': 1}], ({'': 2},), object(), None, 0, '']
        for leaf in leaves:
            with self.subTest(leaf=type(leaf).__name__):
                source = {'a': {'b': leaf}}
                flat = solution.flatten(source)
                self.assertIs(flat['a.b'], leaf)
                nested = solution.unflatten(flat)
                self.assertIs(nested['a']['b'], leaf)
                self.assertIs(source['a']['b'], leaf)


    def test_literal_segments_and_shared_branches(self):
        flat = {'a': 1, 'ab.x': 2, 'ab.y.z': 3, '  .01': 4,
                'A.x': 5, 'aA.x': 6, 'é.值': 7}
        nested = {'a': 1, 'ab': {'x': 2, 'y': {'z': 3}},
                  '  ': {'01': 4}, 'A': {'x': 5}, 'aA': {'x': 6},
                  'é': {'值': 7}}
        self.assertEqual(solution.unflatten(flat), nested)
        self.assertEqual(solution.flatten(nested), flat)
        self.assertEqual(solution.unflatten(dict(reversed(list(flat.items())))), nested)


    def test_flatten_invalid_keys_at_every_depth(self):
        for key in ('', '.', 'a.b', '.a', 'a.'):
            for source in ({key: 1}, {'outer': {key: {}}}):
                with self.subTest(source=source):
                    with self.assertRaises(ValueError):
                        solution.flatten(source)
        for key in (1, None, ('a',)):
            for source in ({key: 1}, {'outer': {key: 2}}):
                with self.assertRaises(TypeError):
                    solution.flatten(source)



    def test_scalar_prefix_conflicts_both_orders(self):
        for prefix, descendant in (('a', 'a.b'), ('a.b', 'a.b.c.d')):
            for value in (None, False, 0, '', [], ()):
                entries = [(prefix, value), (descendant, 2)]
                for ordered in (entries, entries[::-1]):
                    with self.subTest(ordered=ordered):
                        source = dict(ordered)
                        with self.assertRaises(ValueError):
                            solution.unflatten(source)
                        self.assertEqual(list(source.items()), ordered)



if __name__ == '__main__':
    unittest.main()
