import unittest

import solution


class DictSubclass(dict):
    pass


class SolutionTests(unittest.TestCase):
    def test_basic_round_trip(self):
        nested = {'a': {'b': 1, 'c': {'d': None}}, 'x': False}
        flat = {'a.b': 1, 'a.c.d': None, 'x': False}
        self.assertEqual(solution.flatten(nested), flat)
        self.assertEqual(solution.unflatten(flat), nested)
        self.assertEqual(solution.unflatten(solution.flatten(nested)), nested)

    def test_empty_roots(self):
        for function in (solution.flatten, solution.unflatten):
            source = {}
            result = function(source)
            self.assertEqual(result, {})
            self.assertIsNot(result, source)
            self.assertIs(type(result), dict)



    def test_subclasses_and_fresh_containers(self):
        child = DictSubclass(x=1)
        source = DictSubclass(a=child)
        flat = solution.flatten(source)
        self.assertEqual(flat, {'a.x': 1})
        self.assertIs(type(flat), dict)
        nested = solution.unflatten(DictSubclass(flat))
        self.assertIs(type(nested), dict)
        self.assertIs(type(nested['a']), dict)
        self.assertIsNot(nested['a'], child)
        nested['a']['x'] = 2
        self.assertEqual(source, {'a': {'x': 1}})


    def test_non_dict_roots(self):
        for value in (None, [], (), 0, 'a.b'):
            for function in (solution.flatten, solution.unflatten):
                with self.subTest(value=value, function=function.__name__):
                    with self.assertRaises(TypeError):
                        function(value)


    def test_unflatten_invalid_paths(self):
        for key in ('', '.', '.a', 'a.', 'a..b', 'a...b'):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    solution.unflatten({key: 1})
        for key in (1, None, ('a',)):
            with self.assertRaises(TypeError):
                solution.unflatten({key: 1})

    def test_nonempty_flat_dict_values_rejected(self):
        for value in ({'x': 1}, DictSubclass(x={})):
            with self.assertRaises(ValueError):
                solution.unflatten({'a.b': value})


    def test_empty_dict_prefix_conflicts_both_orders(self):
        for prefix, descendant in (('a', 'a.b'), ('a.b', 'a.b.c.d')):
            for leaf in ({}, DictSubclass()):
                entries = [(prefix, leaf), (descendant, {})]
                for ordered in (entries, entries[::-1]):
                    with self.subTest(ordered=ordered):
                        source = dict(ordered)
                        with self.assertRaises(ValueError):
                            solution.unflatten(source)
                        self.assertEqual(source, dict(ordered))
                        self.assertEqual(leaf, {})


if __name__ == '__main__':
    unittest.main()
